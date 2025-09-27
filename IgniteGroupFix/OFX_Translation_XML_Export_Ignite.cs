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
        static readonly string[] DescriptionKeywords = { "Beschreibung:", "Description:", "Descripci\xF3n:", "Description :", "説明：", "설명:", "Opis:", "Descri\xE7\xE3o:", "说明:" };
        static readonly string[] DefaultExtraStrings = { "", ".de-DE", ".en-US", ".es-ES", ".fr-FR", ".ja-JP", ".ko-KR", ".pl-PL", ".pt-BR", ".zh-CN" };

        static string outputFolderPath = Path.Combine(DesktopFolder, "OFX_XML");
        static string blackWhiteListString = "HitFilm";
        static bool blackWhiteList = false;
        static string[] blackWhiteListStrings = blackWhiteListString.Split(';');
        static string extraString = "";
        static int groupMax = 250;

        static Dictionary<string, OfxImageEffectResource> dic = new Dictionary<string, OfxImageEffectResource>();

        public void Main(Vegas vegas)
        {
            myVegas = vegas;

            if (!ShowWindow())
            {
                return;
            }

            blackWhiteListStrings = blackWhiteListString.Split(';');

            if (!Directory.Exists(outputFolderPath))
            {
                try
                {
                    Directory.CreateDirectory(outputFolderPath);
                }
                catch (Exception ex)
                {
                    myVegas.ShowError(ex);
                    return;
                }
            }

            List<PlugInNode> list = new List<PlugInNode>();

            GetOfxPluginNode(list, myVegas.PlugIns);

            using (Project tmpProject = myVegas.CreateEmptyProject())
            {
                using (UndoBlock undo = new UndoBlock(tmpProject, "Undo"))
                {
                    foreach (PlugInNode node in list)
                    {
                        GetInfoFromNode(tmpProject, node);
                    }
                }
            }

            string commonOfxFolder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "Common Files", "OFX"/* , "Plugins" */);
            string vegasOfxFolder = Path.Combine(Path.GetDirectoryName(Application.ExecutablePath)/* , "OFX Video Plug-Ins" */);

            foreach (KeyValuePair<string, OfxImageEffectResource> kvp in dic)
            {
                string fileName = string.Format("{0}{1}.xml", Path.GetFileNameWithoutExtension(kvp.Key), extraString);
                string filePath = Path.Combine(outputFolderPath, fileName);

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

                    filePath = Path.Combine(outputFolderPath, contentsPath, "Resources", fileName);
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

        public static void GetInfoFromNode(Project project, PlugInNode node)
        {
            string uid = Regex.Match(node.UniqueID, @"^{Svfx:(.*)}$").Groups[1].Value;

            if (string.IsNullOrEmpty(uid))
            {
                return;
            }

            bool isMatch = false;
            foreach (string str in blackWhiteListStrings)
            {
                if (!string.IsNullOrEmpty(str) && Regex.IsMatch(uid, str.Trim(' ')))
                {
                    isMatch = true;
                    break;
                }
            }

            if (isMatch == blackWhiteList)
            {
                return;
            }

            Effect ef = new Effect(node);

            VideoTrack trk = project.AddVideoTrack();
            trk.Effects.Add(ef);

            OFXEffect ofxEffect = ef.OFXEffect;
            string path = ofxEffect.PlugInPath;

            OfxImageEffectResource resource = dic.ContainsKey(path) ? dic[path] : null;

            if (resource == null)
            {
                resource = new OfxImageEffectResource();
                dic.Add(path, resource);
            }

            OfxPlugin ofxPlugin = new OfxPlugin { Name = uid };
            resource.Plugins.Add(ofxPlugin);

            string description = ExtractDescription(node.Info);
            OfxResourceSet set = new OfxResourceSet() { Label = node.Name, Grouping = node.Group, Description = description == null ? null : description.Trim(' ').Trim('\n') };
            ofxPlugin.ResourceSets.Add(set);

            OfxImageEffectContext context = new OfxImageEffectContext();
            set.Contexts.Add(context);

            int groupCount = 0;
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

                if (paramBase is OfxParamTypeChoice && para is OFXChoiceParameter && !paramBase.Name.ToLower().Contains("fontindex"))
                {
                    OfxParamTypeChoice choice = paramBase as OfxParamTypeChoice;
                    OFXChoiceParameter choicePara = para as OFXChoiceParameter;
                    foreach (OFXChoice ch in choicePara.Choices)
                    {
                        choice.Options.Add(ch.Name);
                    }
                }

                if (paramBase is OfxParamTypeGroup)
                {
                    string groupName = ReplaceGroupName(paramBase.Name, paramBase.Label);

                    if (groupName.Contains("{0}"))
                    {
                        for (int i = groupCount; i <= groupMax; i++)
                        {
                            OfxParamTypeGroup group = new OfxParamTypeGroup() { Name = string.Format(groupName, i), Label = paramBase.Label, Hint = paramBase.Hint };
                            context.Parameters.Add(group);
                        }
                        groupCount += 1;
                    }

                    else
                    {
                        context.Parameters.Add(paramBase);
                    }

                }
                else
                {
                    context.Parameters.Add(paramBase);
                }
            }
        }

        public static string ReplaceGroupName(string str1, string str2)
        {
            Regex regex = new Regex(@"(\d+)$");

            Match match1 = regex.Match(str1);

            if (!match1.Success)
            {
                return str1;
            }

            string a = match1.Groups[1].Value;
            
            Match match2 = regex.Match(str2);

            string replacement = "{0}";
            if (match2.Success)
            {
                string b = match2.Groups[1].Value;
                if (a.StartsWith(b))
                {
                    replacement = b + replacement;
                }
            }

            string result = regex.Replace(str1, replacement);
            return result;
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

        public bool ShowWindow()
        {
            Form form = new Form
            {
                ShowInTaskbar = false,
                AutoSize = true,
                BackColor = Color.FromArgb(45, 45, 45),
                ForeColor = Color.FromArgb(200, 200, 200),
                Font = new Font("Arial", 9),
                Text = "Ignite Translation XML Export",
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
                Text = outputFolderPath,
                Dock = DockStyle.Fill
            };
            l.Controls.Add(folderTextBox);

            folderButton.Click += delegate (object o, EventArgs e)
            {
                FolderBrowserDialog folderBrowserDialog = new FolderBrowserDialog
                {
                    Description = "Select Output Folder.",
                    SelectedPath = outputFolderPath
                };

                if (folderBrowserDialog.ShowDialog() != DialogResult.OK)
                {
                    return;
                }

                folderTextBox.Text = folderBrowserDialog.SelectedPath;
            };

            Button blackWhiteListButton = new Button
            {
                Text = blackWhiteList ? "Black List" : "White List",
                Margin = new Padding(0, 3, 0, 3),
                TextAlign = ContentAlignment.MiddleCenter,
                AutoSize = true,
                FlatStyle = FlatStyle.Flat,
                Anchor = AnchorStyles.None
            };
            l.Controls.Add(blackWhiteListButton);

            blackWhiteListButton.Click += delegate (object o, EventArgs e)
            {
                blackWhiteList = !blackWhiteList;
                blackWhiteListButton.Text = blackWhiteList ? "Black List" : "White List";
            };

            TextBox blackWhiteListTextBox = new TextBox
            {
                AutoSize = true,
                Margin = new Padding(6, 6, 6, 6),
                Text = blackWhiteListString,
                Dock = DockStyle.Fill
            };
            l.Controls.Add(blackWhiteListTextBox);

            Label label = new Label
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
                Text = extraString
            };
            l.Controls.Add(cb);

            label = new Label
            {
                Margin = new Padding(12, 9, 6, 6),
                Text = "Group Max",
                AutoSize = true
            };
            l.Controls.Add(label);

            TextBox groupMaxTextBox = new TextBox
            {
                AutoSize = true,
                Margin = new Padding(6, 6, 6, 6),
                Text = groupMax.ToString(),
                Dock = DockStyle.Fill
            };
            l.Controls.Add(groupMaxTextBox);

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
            outputFolderPath = folderTextBox.Text;
            extraString = cb.Text;
            blackWhiteListString = blackWhiteListTextBox.Text;
            int max = groupMax;
            groupMax = (int.TryParse(groupMaxTextBox.Text, out max) && max > 0) ? max : groupMax;
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