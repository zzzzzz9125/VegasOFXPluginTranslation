using System;
using System.IO;
using System.Text;
using System.Drawing;
using System.Windows.Forms;
using System.Xml.Serialization;
using System.Collections.Generic;
using System.Text.RegularExpressions;

using ScriptPortal.Vegas;

namespace OfxTrans
{
    public class DoVegas
    {
        public Vegas myVegas;
        static readonly string DesktopFolder = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
        static readonly string DefaultOutputFolder = Path.Combine(DesktopFolder, "OFX_XML");
        static readonly string[] DescriptionKeywords = { "Beschreibung:", "Description:", "Descripci\xF3n:", "Description :", "説明：", "설명:", "Opis:", "Descri\xE7\xE3o:", "说明:" };

        static readonly string DefaultExcludedUid = "";
        static readonly string DefaultExtraString = "";
        static readonly string[] DefaultExtraStrings = { "", ".de-DE", ".en-US", ".es-ES", ".fr-FR", ".ja-JP", ".ko-KR", ".pl-PL", ".pt-BR", ".zh-CN" };

        public void Main(Vegas vegas)
        {
            myVegas = vegas;

            string outputfolder = DefaultOutputFolder;
            string excludedUid = DefaultExcludedUid;
            string extraString = DefaultExtraString;

            if (!ShowWindow(out outputfolder, out excludedUid, out extraString))
            {
                return;
            }

            string[] excludedUids = excludedUid.Split(';');

            if (!Directory.Exists(outputfolder))
            {
                try
                {
                    Directory.CreateDirectory(outputfolder);
                }
                catch (Exception ex)
                {
                    myVegas.ShowError(ex);
                    return;
                }
            }

            List<PlugInNode> list = new List<PlugInNode>();

            GetOfxPluginNode(list, myVegas.PlugIns);

            Dictionary<string, OfxImageEffectResource> dic = new Dictionary<string, OfxImageEffectResource>();

            string uidPattern = @"^{Svfx:(.*)}$";

            using (Project tmpProject = myVegas.CreateEmptyProject())
            {
                using (UndoBlock undo = new UndoBlock(tmpProject, "Undo"))
                {
                    VideoTrack trk = tmpProject.AddVideoTrack();
                    foreach (PlugInNode node in list)
                    {
                        try
                        {
                            Effect ef = new Effect(node);

                            trk.Effects.Add(ef);

                            OFXEffect ofxEffect = ef.OFXEffect;
                            string path = ofxEffect.PlugInPath;

                            OfxImageEffectResource resource = dic.ContainsKey(path) ? dic[path] : null;

                            if (resource == null)
                            {
                                resource = new OfxImageEffectResource();
                                dic.Add(path, resource);
                            }

                            string uid = Regex.Match(node.UniqueID, uidPattern).Groups[1].Value;

                            if (string.IsNullOrEmpty(uid))
                            {
                                continue;
                            }

                            bool isExcluded = false;
                            foreach (string excluded in excludedUids)
                            {
                                if (!string.IsNullOrEmpty(excluded) && Regex.IsMatch(uid, excluded.Trim(' ')))
                                {
                                    isExcluded = true;
                                    break;
                                }
                            }

                            if (isExcluded)
                            {
                                continue;
                            }

                            OfxPlugin ofxPlugin = new OfxPlugin { Name = uid };
                            resource.Plugins.Add(ofxPlugin);

                            string description = ExtractDescription(node.Info);
                            OfxResourceSet set = new OfxResourceSet() { Label = node.Name, Grouping = node.Group, Description = description == null ? null : description.Trim(' ').Trim('\n') };
                            ofxPlugin.ResourceSets.Add(set);

                            OfxImageEffectContext context = new OfxImageEffectContext();
                            set.Contexts.Add(context);

                            foreach (OFXParameter para in ofxEffect.Parameters)
                            {
                                string type = para.ParameterType.ToString(), name = para.Name == null ? null : para.Name.Trim(' ').Trim('\n'), label = para.Label == null ? null : para.Label.Trim(' ').Trim('\n'), hint = para.Hint == null ? null : para.Hint.Trim(' ').Trim('\n');

                                object obj = null;

                                switch (type)
                                {
                                    case "Group": obj = new OfxParamTypeGroup(); break;
                                    case "Boolean": obj = new OfxParamTypeBoolean(); break;
                                    case "Choice": obj = new OfxParamTypeChoice(); break;
                                    case "Custom": obj = new OfxParamTypeCustom(); break;
                                    case "Double2D": obj = new OfxParamTypeDouble2D(); break;
                                    case "Double3D": obj = new OfxParamTypeDouble3D(); break;
                                    case "Double": obj = new OfxParamTypeDouble(); break;
                                    case "Integer2D": obj = new OfxParamTypeInteger2D(); break;
                                    case "Integer3D": obj = new OfxParamTypeInteger3D(); break;
                                    case "Integer": obj = new OfxParamTypeInteger(); break;
                                    case "RGBA": obj = new OfxParamTypeRGBA(); break;
                                    case "RGB": obj = new OfxParamTypeRGB(); break;
                                    case "String": obj = new OfxParamTypeString(); break;
                                    case "PushButton": obj = new OfxParamTypePushButton(); break;
                                    case "16": obj = new OfxParamTypeImage(); break;
                                    default: break;
                                }

                                OfxParamBase paramBase = obj as OfxParamBase;

                                if (paramBase == null || string.IsNullOrEmpty(name) || (string.IsNullOrEmpty(label) && !(paramBase is OfxParamTypeChoice)))
                                {
                                    continue;
                                }

                                paramBase.Name = name;
                                paramBase.Label = label;
                                paramBase.Hint = hint;

                                if (paramBase is OfxParamTypeChoice && para is OFXChoiceParameter)
                                {
                                    OfxParamTypeChoice choice = paramBase as OfxParamTypeChoice;
                                    OFXChoiceParameter choicePara = para as OFXChoiceParameter;
                                    foreach (OFXChoice ch in choicePara.Choices)
                                    {
                                        choice.Options.Add(ch.Name);
                                    }
                                }

                                context.Parameters.Add(paramBase);
                            }
                        }
                        catch { continue; }
                    }
                }
            }

            string commonOfxFolder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "Common Files", "OFX"/* , "Plugins" */);
            string vegasOfxFolder = Path.Combine(Path.GetDirectoryName(Application.ExecutablePath)/* , "OFX Video Plug-Ins" */);

            foreach (KeyValuePair<string, OfxImageEffectResource> kvp in dic)
            {
                string fileName = string.Format("{0}{1}.xml", Path.GetFileNameWithoutExtension(kvp.Key), extraString);
                string filePath = Path.Combine(outputfolder, fileName);

                string prefix = commonOfxFolder;
                if (!kvp.Key.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
                {
                    prefix = vegasOfxFolder;
                    if (!kvp.Key.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
                    {
                        prefix = "";
                    }
                }

                if (!string.IsNullOrEmpty(prefix))
                {
                    string relativePath = kvp.Key.Substring(prefix.Length);

                    if (!prefix.EndsWith(@"\") && !relativePath.StartsWith(@"\"))
                    {
                        relativePath = @"\" + relativePath;
                    }

                    string contentsPath = Path.GetDirectoryName(Path.GetDirectoryName(relativePath.TrimStart('\\')));

                    filePath = Path.Combine(outputfolder, contentsPath, "Resources", fileName);
                }

                string dir = Path.GetDirectoryName(filePath);
                if (!Directory.Exists(dir))
                {
                    Directory.CreateDirectory(dir);
                }

                kvp.Value.SortPluginsByName();

                string xml = SerializeXml(kvp.Value);
                File.WriteAllText(filePath, xml);
            }

            MessageBox.Show("Done.");
        }

        public static string ExtractDescription(string str)
        {
            if (string.IsNullOrEmpty(str))
            {
                return null;
            }

            int minIndex = int.MaxValue;
            string foundKeyword = null;

            foreach (string keyword in DescriptionKeywords)
            {
                int index = str.IndexOf(keyword);
                if (index >= 0 && index < minIndex)
                {
                    minIndex = index;
                    foundKeyword = keyword;
                }
            }

            if (foundKeyword != null)
            {
                return str.Substring(minIndex + foundKeyword.Length).TrimStart(' ');
            }

            return null;
        }

        public void GetOfxPluginNode(List<PlugInNode> list, PlugInNode node)
        {
            foreach (PlugInNode p in node)
            {
                if (p.IsContainer)
                {
                    GetOfxPluginNode(list, p);
                }
                else if (p.IsOFX)
                {
                    bool repeated = false;
                    foreach (PlugInNode tmp in list)
                    {
                        if (tmp.UniqueID == p.UniqueID)
                        {
                            repeated = true;
                        }
                    }
                    if (!repeated)
                    {
                        list.Add(p);
                    }
                }
            }
        }

        public static string SerializeXml(object data)
        {
            using (MemoryStream ms = new MemoryStream())
            {
                using (StreamWriter textWriter = new StreamWriter(ms, new UTF8Encoding()))
                {
                    XmlSerializer serializer = new XmlSerializer(data.GetType());

                    XmlSerializerNamespaces ns = new XmlSerializerNamespaces();
                    ns.Add("", "");

                    serializer.Serialize(textWriter, data, ns);

                    return Encoding.UTF8.GetString(ms.GetBuffer(), 0, (int)ms.Length);
                }
            }
        }

        public bool ShowWindow(out string folderPath, out string excludedUid, out string extraString)
        {
            Form form = new Form
            {
                ShowInTaskbar = false,
                AutoSize = true,
                BackColor = Color.FromArgb(45, 45, 45),
                ForeColor = Color.FromArgb(200, 200, 200),
                Font = new Font("Arial", 9),
                Text = "OFX Translation XML Export",
                FormBorderStyle = FormBorderStyle.FixedToolWindow,
                StartPosition = FormStartPosition.CenterScreen,
                AutoSizeMode = AutoSizeMode.GrowAndShrink
            };

            Panel p = new Panel
            {
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink
            };
            form.Controls.Add(p);

            TableLayoutPanel l = new TableLayoutPanel
            {
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                GrowStyle = TableLayoutPanelGrowStyle.AddRows,
                ColumnCount = 2
            };
            p.Controls.Add(l);

            Button folderButton = new Button
            {
                Text = "Output Folder",
                Margin = new Padding(0, 3, 0, 3),
                TextAlign = ContentAlignment.MiddleCenter,
                AutoSize = true,
                FlatStyle = FlatStyle.Flat,
                Anchor = AnchorStyles.None
            };
            l.Controls.Add(folderButton);

            TextBox folderTextBox = new TextBox
            {
                AutoSize = true,
                Margin = new Padding(6, 6, 6, 6),
                Text = DefaultOutputFolder,
                Dock = DockStyle.Fill
            };
            l.Controls.Add(folderTextBox);

            folderButton.Click += delegate (object o, EventArgs e)
            {
                FolderBrowserDialog folderBrowserDialog = new FolderBrowserDialog
                {
                    Description = "Select Output Folder.",
                    SelectedPath = DefaultOutputFolder
                };

                if (folderBrowserDialog.ShowDialog() != DialogResult.OK)
                {
                    return;
                }

                folderTextBox.Text = folderBrowserDialog.SelectedPath;
            };

            Label label = new Label
            {
                Margin = new Padding(12, 9, 6, 6),
                Text = "Excluded UID",
                AutoSize = true
            };
            l.Controls.Add(label);

            TextBox excludedUidTextBox = new TextBox
            {
                AutoSize = true,
                Margin = new Padding(6, 6, 6, 6),
                Text = DefaultExcludedUid,
                Dock = DockStyle.Fill
            };
            l.Controls.Add(excludedUidTextBox);

            label = new Label
            {
                Margin = new Padding(12, 9, 6, 6),
                Text = "Extra String",
                AutoSize = true
            };
            l.Controls.Add(label);

            ComboBox cb = new ComboBox()
            {
                DataSource = DefaultExtraStrings,
                DropDownStyle = ComboBoxStyle.DropDown,
                Margin = new Padding(6, 6, 6, 6),
                Dock = DockStyle.Fill,
                Text = DefaultExtraString
            };
            l.Controls.Add(cb);

            FlowLayoutPanel panel = new FlowLayoutPanel
            {
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                Anchor = AnchorStyles.None,
                Font = new Font("Arial", 8)
            };
            l.Controls.Add(panel);
            l.SetColumnSpan(panel, 2);

            Button ok = new Button
            {
                Text = "OK",
                DialogResult = DialogResult.OK
            };
            panel.Controls.Add(ok);
            form.AcceptButton = ok;

            Button cancel = new Button
            {
                Text = "Cancel",
                DialogResult = DialogResult.Cancel
            };
            panel.Controls.Add(cancel);
            form.CancelButton = cancel;

            DialogResult result = form.ShowDialog(myVegas.MainWindow);
            folderPath = folderTextBox.Text;
            excludedUid = excludedUidTextBox.Text;
            extraString = cb.Text;
            return result == DialogResult.OK;
        }
    }

    public class OfxPluginNameComparer : IComparer<OfxPlugin>
    {
        public int Compare(OfxPlugin x, OfxPlugin y)
        {
            if (x == null && y == null) return 0;
            if (x == null) return -1;
            if (y == null) return 1;

            return string.Compare(x.Name, y.Name, StringComparison.Ordinal);
        }
    }

    [XmlRoot("OfxImageEffectResource")]
    public class OfxImageEffectResource
    {
        [XmlElement("OfxPlugin")]
        public List<OfxPlugin> Plugins { get; set; }

        public OfxImageEffectResource()
        {
            Plugins = new List<OfxPlugin>();
        }

        public void SortPluginsByName()
        {
            Plugins.Sort(new OfxPluginNameComparer());
        }
    }

    public class OfxPlugin
    {
        [XmlAttribute("name")]
        public string Name { get; set; }

        [XmlElement("OfxResourceSet")]
        public List<OfxResourceSet> ResourceSets { get; set; }

        public OfxPlugin()
        {
            ResourceSets = new List<OfxResourceSet>();
        }
    }

    public class OfxResourceSet
    {
        [XmlAttribute("ofxHost")]
        public string OfxHost { get; set; }

        [XmlElement("OfxPropLabel")]
        public string Label { get; set; }

        [XmlElement("OfxImageEffectPluginPropGrouping")]
        public string Grouping { get; set; }

        [XmlElement("OfxPropPluginDescription")]
        public string Description { get; set; }

        [XmlElement("OfxImageEffectContext")]
        public List<OfxImageEffectContext> Contexts { get; set; }

        public OfxResourceSet()
        {
            OfxHost = "default";
            Contexts = new List<OfxImageEffectContext>();
        }
    }

    public class OfxImageEffectContext
    {
        [XmlAttribute("name")]
        public string Name { get; set; }

        [XmlElement("OfxParamTypeGroup", typeof(OfxParamTypeGroup))]
        [XmlElement("OfxParamTypeBoolean", typeof(OfxParamTypeBoolean))]
        [XmlElement("OfxParamTypeChoice", typeof(OfxParamTypeChoice))]
        [XmlElement("OfxParamTypeCustom", typeof(OfxParamTypeCustom))]
        [XmlElement("OfxParamTypeDouble2D", typeof(OfxParamTypeDouble2D))]
        [XmlElement("OfxParamTypeDouble3D", typeof(OfxParamTypeDouble3D))]
        [XmlElement("OfxParamTypeDouble", typeof(OfxParamTypeDouble))]
        [XmlElement("OfxParamTypeInteger2D", typeof(OfxParamTypeInteger2D))]
        [XmlElement("OfxParamTypeInteger3D", typeof(OfxParamTypeInteger3D))]
        [XmlElement("OfxParamTypeInteger", typeof(OfxParamTypeInteger))]
        [XmlElement("OfxParamTypeRGBA", typeof(OfxParamTypeRGBA))]
        [XmlElement("OfxParamTypeRGB", typeof(OfxParamTypeRGB))]
        [XmlElement("OfxParamTypeString", typeof(OfxParamTypeString))]
        [XmlElement("OfxParamTypePushButton", typeof(OfxParamTypePushButton))]
        [XmlElement("OfxParamTypeImage", typeof(OfxParamTypeImage))]
        /* [XmlElement("OfxMessage", typeof(OfxMessage))] */
        public List<OfxParamBase> Parameters { get; set; }

        public OfxImageEffectContext()
        {
            Name = "default";
            Parameters = new List<OfxParamBase>();
        }
    }

    [XmlInclude(typeof(OfxParamTypeGroup))]
    [XmlInclude(typeof(OfxParamTypeDouble))]
    [XmlInclude(typeof(OfxParamTypeBoolean))]
    [XmlInclude(typeof(OfxParamTypeRGBA))]
    [XmlInclude(typeof(OfxParamTypeRGB))]
    [XmlInclude(typeof(OfxParamTypeChoice))]
    [XmlInclude(typeof(OfxParamTypePushButton))]
    [XmlInclude(typeof(OfxParamTypeImage))]
    [XmlInclude(typeof(OfxParamTypeInteger))]
    [XmlInclude(typeof(OfxParamTypeDouble2D))]
    [XmlInclude(typeof(OfxParamTypeDouble3D))]
    [XmlInclude(typeof(OfxParamTypeString))]
    /* [XmlInclude(typeof(OfxMessage))] */
    public abstract class OfxParamBase
    {
        [XmlAttribute("name")]
        public string Name { get; set; }

        [XmlElement("OfxPropLabel")]
        public string Label { get; set; }

        [XmlElement("OfxParamPropHint")]
        public string Hint { get; set; }
    }

    public class OfxParamTypeGroup : OfxParamBase { }

    public class OfxParamTypeBoolean : OfxParamBase { }

    public class OfxParamTypeChoice : OfxParamBase
    {
        [XmlElement("OfxParamPropChoiceOption")]
        public List<string> Options { get; set; }

        public OfxParamTypeChoice()
        {
            Options = new List<string>();
        }
    }

    public class OfxParamTypeCustom : OfxParamBase { }

    public class OfxParamTypeDouble2D : OfxParamBase { }

    public class OfxParamTypeDouble3D : OfxParamBase { }

    public class OfxParamTypeDouble : OfxParamBase { }

    public class OfxParamTypeInteger2D : OfxParamBase { }

    public class OfxParamTypeInteger3D : OfxParamBase { }

    public class OfxParamTypeInteger : OfxParamBase { }

    public class OfxParamTypeRGBA : OfxParamBase { }

    public class OfxParamTypeRGB : OfxParamBase { }

    public class OfxParamTypeString : OfxParamBase { }

    public class OfxParamTypePushButton : OfxParamBase { }

    public class OfxParamTypeImage : OfxParamBase { }

    /* public class OfxMessage : OfxParamBase
    {
        [XmlText]
        public string Text { get; set; }
    } */
}

public class EntryPoint
{
    public void FromVegas(Vegas vegas)
    {
        OfxTrans.DoVegas doVegas = new OfxTrans.DoVegas();
        doVegas.Main(vegas);
    }
}