import json

with open("/home/agi/code/xmat_db/fbmat.json") as file:
	db = json.load(file)

frame = \
"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom' xmlns:apps='http://schemas.google.com/apps/2006'>
	<title>Imported Filters</title>
	<author>
		<name>Tomas Krnak</name>
		<email>tomas@krnak.cz</email>
	</author>
{rules}
</feed>
"""
rule = \
"""	<entry>
		<category term='filter'></category>
		<title>Imported Filter</title>
		<content></content>
		<apps:property name='from' value='agipybot@gmail.com'/>
		<apps:property name='hasTheWord' value='{word}'/>
		<apps:property name='label' value='{label}'/>
		<apps:property name='shouldMarkAsRead' value='{read}'/>
		<apps:property name='shouldArchive' value='{archive}'/>
		<apps:property name='sizeOperator' value='s_sl'/>
		<apps:property name='sizeUnit' value='s_smb'/>
	</entry>
"""

def group_to_rules(group_info):
	rules = ""
	priority = group_info["priority"]
	label    = group_info["label"]
	priority
	if 0 < priority:
		rules += rule.format(
			word="lab"+label,
			label="fb/"+label,
			read=str(priority<2).lower(),
			archive=str(priority<4).lower()
			)
	return rules

group_rules = "".join(map(group_to_rules,db["groups"].values()))

priority_rules = "".join([
	rule.format(
		word="lab"+str(i)+"priority",
		label=str(i)+"priority",
		read="false",
		archive="false"
		)
	for i in range(1,6)])

with open("rules_to_import.xml", "w") as file:
	file.write(frame.format(
		rules=priority_rules+group_rules))
