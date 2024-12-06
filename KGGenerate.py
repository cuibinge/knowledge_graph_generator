# Import related packages
from knowledge_graph_builder import EAOntology, EROntology
from sympy import erf
import pandas as pd
import os


# Define Entity Relationship Ontology
def define_ERontology():
    return EROntology(
        entities=[
            {"植物": "红树,芦苇,互花米草,碱蓬,盐地碱蓬,盐角草,獐毛,蒲公英,柽柳,稻,丛枝蓼,川蔓藻,刺槐,刺苋,大叶藻,地榆,繁缕,拂子茅,浮萍,甘草,杠柳,狗牙根,构,黑藻,碱茅,金鱼藻,决明,苦草,苦荬菜,荔枝草,木榄,海莲,滨麦，秋英"},
            {"水体": "海水, 潮沟, 池塘, 河流, 湖泊, 湿地池, 沼泽"},
            {"滩涂": "滩涂,潮滩"},
            {"农田": "旱耕地, 水浇地"},
            {"湿地": "海滩盐沼"},
            {"属": "蓼属,川蔓藻属,稻属"},
            {"科": "菊科,泽泻科,苋科,豆科,禾本科,蓼科，川蔓藻科"},
            {"界":"植物界"},
            {"门":"被子植物门,绿藻门,红藻门"},
            {"纲":"木兰纲,双子叶植物纲,单子叶植物纲,木贼纲"},
            {"目":"菊目,泽泻目,石竹目,豆目,禾本目"},
            {"群落":"草甸,红树林群落,香蒲群落,海草床群落，潮上带群落,潮间带群落，白茅群落,芦苇群落,盐沼群落,棒头草群落,凤眼莲群落,空心莲子草群落,眼子菜群落,酸模叶蓼群落,大薸群落"},
        ],
        relationships=[
            "邻近",
            "生长",
            "界",
            "门",
            "纲",
            "目",
            "科",
            "属",
            "别名",
            "俗名",
            "优势种",
            "伴生种",
        ]
)

# Define Entity Attribute Ontology
def define_EAontology():
    return EAOntology(
        entities=[
            {"植物": "红树,芦苇,互花米草,碱蓬,盐地碱蓬,盐角草,獐毛,蒲公英,柽柳,稻,丛枝蓼,川蔓藻,刺槐,刺苋,大叶藻,地榆,繁缕,拂子茅,浮萍,甘草,杠柳,狗牙根,构,黑藻,碱茅,金鱼藻,决明,苦草,苦荬菜,荔枝草,木榄,海莲,滨麦，秋英"},
            {"水体": "海水, 潮沟, 池塘, 河流, 湖泊, 湿地池, 沼泽"},
            {"滩涂": "滩涂,潮滩"},
            {"湿地": "海滩盐沼"},{"群落":"草甸,红树林群落,香蒲群落,海草床群落，潮上带群落,潮间带群落，白茅群落,芦苇群落,盐沼群落,棒头草群落,凤眼莲群落,空心莲子草群落,眼子菜群落,酸模叶蓼群落,大薸群落"},
        ],
        attributes=[
            {"生活型": "多年生草本植物,一年生草本植物,一年或二年生草本植物,乔木或灌木,多年生沉水草本植物"},
            {"高度": "45-100厘米"},
            {"盖度": "75-90%,100%"},
            {"颜色": "深蓝色,绿色,粉红色"},
            {"染色体": "2n=30"},
            {"花": "花单生，盛开时长约3厘米，花梗萼平滑无棱，暗黄红色，花柱棱柱形，长约2厘米，黄色且柱头有裂；"},
            {"学名": "yrrhiza uralensis Fisch."},
            {"茎": "茎直立，颜色为绿色，表面光滑。"},
            {"叶": "叶椭圆状长圆形，长达15厘米，先端短尖，基部楔形；"},
            {"花": "花序圆锥状疏展，花色为淡黄色，长约30厘米，分枝多，棱粗糙，在成熟期弯垂，小穗两侧扁，为长圆状卵形或椭圆形，长约1厘米，宽2-4毫米，花药长2-3毫米。"},
            {"果实": "果实为谷粒，呈卵形或椭圆形对圆筒状，颜色为米白色或金黄色，长约5毫米，宽约2毫米，厚1-1.5毫米。"},
            {"种子": "种子矩圆状卵形，种皮近革质，有钩状刺毛，直径约1.5毫米。"},
            {"功效": "全草可入药，有清血、解热、生肌之效。"},
            {"物候期": "花期4-5月，果期6-7月。"},
            {"用途": "韧皮纤维可作造纸材料"},
            {"作用": "沼泽在维护生态系统稳定性、促进水循环和提供养分方面具有重要作用。滨海湿地草甸在水质净化、洪水调节和土壤保持方面发挥着重要作用，能够过滤污染物，减少水土流失。"},
            {"生境":"生于轻度盐碱性湿润草地、田边、水溪、河谷、低草甸盐化沙地。"},  
        ]
    )

# Load the user input txt
def load_usertext(inputfile):
    with open(inputfile, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        user_text = ["\n" + line.strip() + "\n" for line in lines if line.strip()]
    return user_text 


def export_to_directory(graph, ontology, output_dir):
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define file the name
    ER_filename = "ERTriples.xlsx"
    EA_filename = "EATriples.xlsx"
    
    # Build a complete file path
    ER_outputfile = os.path.join(output_dir, ER_filename)
    EA_outputfile = os.path.join(output_dir, EA_filename)
    
    # Extracting Entity Relationship Triples
    ER_extracted_data = [
        [edge.node_1.entity, edge.node_1.name, edge.node_2.entity, edge.node_2.name, edge.relationship]
        for edge in graph
        if isinstance(ontology, EROntology)  
    ]
    # Extracting Entity Attribute Triples
    EA_extracted_data = [
        [edge.node_1.entity, edge.node_1.name, edge.node_2.attribute, edge.node_2.name, edge.relationship]
        for edge in graph
        if isinstance(ontology, EAOntology)  
    ]
    
    # Write Entity Relationship Triples to Excel
    if ER_extracted_data:
        ER_df = pd.DataFrame(ER_extracted_data, columns=['head', 'key1', 'tail', 'key2', 'relationship'])
        ER_df = ER_df[['head', 'key1', 'relationship', 'tail', 'key2']]
        ER_fileexists = os.path.isfile(ER_outputfile)
        if not ER_fileexists:
            ER_df.to_excel(ER_outputfile, index=False)
        else:
            with pd.ExcelWriter(ER_outputfile, mode='a', if_sheet_exists='overlay') as writer:
                existing_df_er = pd.read_excel(ER_outputfile)
                combined_df_er = pd.concat([existing_df_er, ER_df], ignore_index=True)
                combined_df_er.to_excel(writer, index=False)
    
    # Write Entity Attribute Triples to Excel
    if EA_extracted_data:
        EA_df = pd.DataFrame(EA_extracted_data, columns=['head', 'key1', 'tail', 'key2', 'attribute'])
        EA_df = EA_df[['head', 'key1', 'attribute', 'tail', 'key2']]
        EA_fileexists = os.path.isfile(EA_outputfile)
        if not EA_fileexists:
            EA_df.to_excel(EA_outputfile, index=False)
        else:
            with pd.ExcelWriter(EA_outputfile, mode='a', if_sheet_exists='overlay') as writer:
                existing_df_ea = pd.read_excel(EA_outputfile)
                combined_df_ea = pd.concat([existing_df_ea, EA_df], ignore_index=True)
                combined_df_ea.to_excel(writer, index=False)

            

            



