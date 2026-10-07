--[[ Custom-item tooltip template
	Keep normal text dark and use the light-cyan divider between logical groups.
	Required order: description, properties, type/weight/level/job.
	Do not put Thai text directly in the CP874 runtime file; edit this UTF-8
	source and transcode it with an explicit CP874 encoder.

	[ID] = {
		unidentifiedDisplayName = "Unknown Item",
		unidentifiedResourceName = "",
		unidentifiedDescriptionName = { "" },
		identifiedDisplayName = "Item",
		identifiedResourceName = "",
		identifiedDescriptionName = {
			-- Keep this as one concatenated value. Separate table entries make
			-- this client add unwanted vertical gaps between visible lines.
			"^111111คำอธิบายไอเทม^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111คุณสมบัติไอเทม^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ...^000000\n" ..
			"^111111น้ำหนัก: ...^000000\n" ..
			"^111111เลเวลที่ต้องการ: ...^000000\n" ..
			"^111111อาชีพ: ...^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
]]

-- Table for Custom Items
local function cloneNewPlayerNotForSale(sourceId, displayName)
	local source = tbl[sourceId]
	local item = {}
	for key, value in pairs(source) do
		item[key] = value
	end
	item.unidentifiedDisplayName = displayName
	item.identifiedDisplayName = displayName
	return item
end

tbl_custom = {
	[902250] = {
		unidentifiedDisplayName = "Costume 1 Gacha Egg",
		unidentifiedResourceName = "mid_gacha1_egg",
		unidentifiedDescriptionName = { "An egg containing one Costume 1 Gacha draw." },
		identifiedDisplayName = "Costume 1 Gacha Egg",
		identifiedResourceName = "mid_gacha1_egg",
		identifiedDescriptionName = {
			"^FFD700Costume 1 Gacha Egg^000000\n" ..
			"^111111Open to make one draw from the Costume 1 Gacha NPC reward table.^000000\n" ..
			"^00AAFFUses the same Costume 1 pity counter as the Gacha NPC.^000000\n" ..
			"^00AAFFFeatured reward rate: 6.90%; guaranteed featured reward on the 20th draw.^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111The egg is not consumed if inventory weight or slots are insufficient.^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111Type: Consumable Box | Weight: 0.1^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902251] = {
		unidentifiedDisplayName = "Costume 2 Gacha Egg",
		unidentifiedResourceName = "mid_gacha2_egg",
		unidentifiedDescriptionName = { "An egg containing one Costume 2 Gacha draw." },
		identifiedDisplayName = "Costume 2 Gacha Egg",
		identifiedResourceName = "mid_gacha2_egg",
		identifiedDescriptionName = {
			"^FFD700Costume 2 Gacha Egg^000000\n" ..
			"^111111Open to make one draw from the Costume 2 Gacha NPC reward table.^000000\n" ..
			"^00AAFFUses the same Costume 2 pity counter as the Gacha NPC.^000000\n" ..
			"^00AAFFFeatured reward rate: 7.20%; guaranteed featured reward on the 20th draw.^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111The egg is not consumed if inventory weight or slots are insufficient.^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111Type: Consumable Box | Weight: 0.1^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902252] = {
		unidentifiedDisplayName = "Shadow Gacha Egg",
		unidentifiedResourceName = "mid_shadow_egg",
		unidentifiedDescriptionName = { "An egg containing one Promotion Shadow Gacha draw." },
		identifiedDisplayName = "Shadow Gacha Egg",
		identifiedResourceName = "mid_shadow_egg",
		identifiedDescriptionName = {
			"^FFD700Shadow Gacha Egg^000000\n" ..
			"^111111Open to make one draw from the Promotion Shadow Gacha NPC reward table.^000000\n" ..
			"^00AAFFUses the same Promotion Shadow pity counter as the Gacha NPC.^000000\n" ..
			"^00AAFFFeatured reward rate: 6.00%; guaranteed featured reward on the 20th draw.^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111The egg is not consumed if inventory weight or slots are insufficient.^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111Type: Consumable Box | Weight: 0.1^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902266] = {
		unidentifiedDisplayName = "Midnight Shadow Exchange Ticket",
		unidentifiedResourceName = "midnight_shadow_exchange_ticket",
		unidentifiedDescriptionName = { "ตั๋วสำหรับแลกรับ Promotion Shadow ที่เลือกได้ 1 ชิ้น" },
		identifiedDisplayName = "Midnight Shadow Exchange Ticket",
		identifiedResourceName = "midnight_shadow_exchange_ticket",
		identifiedDescriptionName = {
			"^FFD700ตั๋วแลก Promotion Shadow^000000\n" ..
			"^111111ใช้แลกรับ Promotion Shadow 1 ชิ้นจากทั้งหมด 6 ชิ้นที่ NPC ผู้ดูแลกาชา เมือง Morocc^000000\n" ..
			"^00AAFFได้จากการย่อย Promotion Shadow ที่ระบุแล้ว 3 ชิ้น: ไม่สวมใส่, +0, ไม่เสียหาย, ไม่มีการ์ด, Enchant Grade หรือ Random Option^000000\n" ..
			"^00AAFFผูกกับบัญชี^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมทั่วไป | น้ำหนัก: 0.1^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902249] = {
		unidentifiedDisplayName = "Midnight Fly Wing Box (200)",
		unidentifiedResourceName = "\191\192\183\161\181\200\186\184\182\243\187\243\192\218",
		unidentifiedDescriptionName = { "A box containing 200 Fly Wings." },
		identifiedDisplayName = "Midnight Fly Wing Box (200)",
		identifiedResourceName = "\191\192\183\161\181\200\186\184\182\243\187\243\192\218",
		identifiedDescriptionName = {
			"^FFD700Midnight Fly Wing Box (200)^000000\n" ..
			"^111111Open this box to receive 200 Fly Wings.^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111The box will not be consumed if inventory weight or slots are insufficient.^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111Type: Consumable Box | Weight: 0.1^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902247] = {
		unidentifiedDisplayName = "Moon Fragment",
		unidentifiedResourceName = "moon_fragment",
		unidentifiedDescriptionName = { "เศษเสี้ยวคริสตัลจันทราที่เปล่งประกายลึกลับ" },
		identifiedDisplayName = "Moon Fragment",
		identifiedResourceName = "moon_fragment",
		identifiedDescriptionName = {
			"^FFD700Moon Fragment^000000\n" ..
			"^111111เศษเสี้ยวคริสตัลจันทราที่เปล่งประกายลึกลับ^000000\n" ..
			"^111111เป็นเศษแสงจากโลกที่ตื่นขึ้นหลังพระอาทิตย์ตกดิน^000000\n" ..
			"^111111พบได้จากสิ่งมีชีวิตพิเศษในยามค่ำคืนเท่านั้น^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^00AAFFวัตถุดิบสำคัญสำหรับกิจกรรม Midnight Event^000000\n" ..
			"^111111สามารถใช้แลกเปลี่ยนของรางวัลกับ Midnight Keeper ได้^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมเบ็ดเตล็ด | น้ำหนัก: 1^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902248] = {
		unidentifiedDisplayName = "Moonlit Dust",
		unidentifiedResourceName = "moonlit_dust",
		unidentifiedDescriptionName = { "ผงละอองเรืองแสงระยิบระยับดั่งแสงดาวค่ำคืน" },
		identifiedDisplayName = "Moonlit Dust",
		identifiedResourceName = "moonlit_dust",
		identifiedDescriptionName = {
			"^FFD700Moonlit Dust^000000\n" ..
			"^111111ผงละอองเรืองแสงระยิบระยับดั่งแสงดาวค่ำคืน^000000\n" ..
			"^111111ร่วงหล่นจากมอนสเตอร์พิเศษของ Midnight RO^000000\n" ..
			"^111111มีพลังงานมนตราแห่งราตรีกาลแฝงอยู่อย่างเข้มข้น^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^00AAFFวัตถุดิบและของสะสมพิเศษสำหรับกิจกรรมในอนาคต^000000\n" ..
			"^111111สามารถเก็บสะสมไว้ในกระเป๋าหรือคลังได้^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมเบ็ดเตล็ด | น้ำหนัก: 1^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902240] = {
		unidentifiedDisplayName = "Midnight VIP Box [7 Days]",
		unidentifiedResourceName = "midnight_vip_box_7",
		unidentifiedDescriptionName = { "กล่อง Midnight VIP ภายในมีบัตร VIP และ Midnight VIP Service" },
		identifiedDisplayName = "Midnight VIP Box [7 Days]",
		identifiedResourceName = "midnight_vip_box_7",
		identifiedDescriptionName = {
			"^FFD700Midnight VIP Box [7 Days]^000000\n" ..
			"^111111เปิดกล่องเพื่อรับไอเทมดังต่อไปนี้^000000\n" ..
			"^00AAFFMidnight VIP Card [7 Days] จำนวน 1 ใบ^000000\n" ..
			"^00AAFFMidnight VIP Service จำนวน 1 ชิ้น^000000\n" ..
			"^111111Service จะไม่แจกซ้ำ หากมีอยู่ในกระเป๋าหรือคลังบัญชี^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^FF7777กล่องนี้ยังไม่เปิดสถานะ VIP โดยตรง^000000\n" ..
			"^111111ใช้บัตร VIP ที่ได้รับเพื่อเปิดสถานะ VIP ทั้งบัญชี^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมกล่อง | น้ำหนัก: 0^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902241] = {
		unidentifiedDisplayName = "Midnight VIP Box [15 Days]",
		unidentifiedResourceName = "midnight_vip_box_15",
		unidentifiedDescriptionName = { "กล่อง Midnight VIP ภายในมีบัตร VIP และ Midnight VIP Service" },
		identifiedDisplayName = "Midnight VIP Box [15 Days]",
		identifiedResourceName = "midnight_vip_box_15",
		identifiedDescriptionName = {
			"^FFD700Midnight VIP Box [15 Days]^000000\n" ..
			"^111111เปิดกล่องเพื่อรับไอเทมดังต่อไปนี้^000000\n" ..
			"^00AAFFMidnight VIP Card [15 Days] จำนวน 1 ใบ^000000\n" ..
			"^00AAFFMidnight VIP Service จำนวน 1 ชิ้น^000000\n" ..
			"^111111Service จะไม่แจกซ้ำ หากมีอยู่ในกระเป๋าหรือคลังบัญชี^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^FF7777กล่องนี้ยังไม่เปิดสถานะ VIP โดยตรง^000000\n" ..
			"^111111ใช้บัตร VIP ที่ได้รับเพื่อเปิดสถานะ VIP ทั้งบัญชี^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมกล่อง | น้ำหนัก: 0^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902242] = {
		unidentifiedDisplayName = "Midnight VIP Box [30 Days]",
		unidentifiedResourceName = "midnight_vip_box_30",
		unidentifiedDescriptionName = { "กล่อง Midnight VIP ภายในมีบัตร VIP และ Midnight VIP Service" },
		identifiedDisplayName = "Midnight VIP Box [30 Days]",
		identifiedResourceName = "midnight_vip_box_30",
		identifiedDescriptionName = {
			"^FFD700Midnight VIP Box [30 Days]^000000\n" ..
			"^111111เปิดกล่องเพื่อรับไอเทมดังต่อไปนี้^000000\n" ..
			"^00AAFFMidnight VIP Card [30 Days] จำนวน 1 ใบ^000000\n" ..
			"^00AAFFMidnight VIP Service จำนวน 1 ชิ้น^000000\n" ..
			"^111111Service จะไม่แจกซ้ำ หากมีอยู่ในกระเป๋าหรือคลังบัญชี^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^FF7777กล่องนี้ยังไม่เปิดสถานะ VIP โดยตรง^000000\n" ..
			"^111111ใช้บัตร VIP ที่ได้รับเพื่อเปิดสถานะ VIP ทั้งบัญชี^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมกล่อง | น้ำหนัก: 0^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902243] = {
		unidentifiedDisplayName = "Midnight VIP Service",
		unidentifiedResourceName = "VIP_Black_Card",
		unidentifiedDescriptionName = { "เปิดเมนูเลือกเรียก NPC สำหรับบัญชี Midnight VIP" },
		identifiedDisplayName = "Midnight VIP Service",
		identifiedResourceName = "VIP_Black_Card",
		identifiedDescriptionName = {
			"^FFD700Midnight VIP Service^000000\n" ..
			"^111111เมื่อใช้งาน จะเปิดเมนูให้เลือก NPC ที่ต้องการเรียก^000000\n" ..
			"^00AAFFตัวเลือก: NPC คาฟร่าส่วนตัว หรือ NPC บัฟ VIP^000000\n" ..
			"^111111NPC ที่เลือกจะปรากฏข้างตัวละครและใช้ได้เฉพาะเจ้าของ^000000\n" ..
			"^111111ใช้งานได้เฉพาะเมื่อสถานะ VIP ยังไม่หมดอายุ^000000\n" ..
			"^111111ไอเทมไม่หายเมื่อใช้งาน และแต่ละบริการมีคูลดาวน์^000000\n" ..
			"^111111สามารถเก็บในคลังบัญชีเพื่อใช้กับตัวละครอื่นได้^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมใช้งานซ้ำ | น้ำหนัก: 0^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902244] = {
		unidentifiedDisplayName = "Midnight VIP Card [7 Days]",
		unidentifiedResourceName = "midnight_vip_7",
		unidentifiedDescriptionName = { "บัตรสำหรับเปิดสถานะ Midnight VIP 7 วัน" },
		identifiedDisplayName = "Midnight VIP Card [7 Days]",
		identifiedResourceName = "midnight_vip_7",
		identifiedDescriptionName = {
			"^FFD700Midnight VIP Card [7 Days]^000000\n" ..
			"^111111ใช้เพื่อเพิ่มสถานะ VIP ให้ทั้งบัญชี^000000\n" ..
			"^00AAFFระยะเวลาใช้งาน 7 วัน^000000\n" ..
			"^111111หากมี VIP อยู่แล้ว ระยะเวลาจะสะสมต่อจากเดิม^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111บัตรจะหายเมื่อระบบยืนยันเวลา VIP สำเร็จเท่านั้น^000000\n" ..
			"^111111สถานะ VIP ใช้ร่วมกันทุกตัวละครในบัญชี^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมใช้งาน | น้ำหนัก: 0^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902245] = {
		unidentifiedDisplayName = "Midnight VIP Card [15 Days]",
		unidentifiedResourceName = "midnight_vip_15",
		unidentifiedDescriptionName = { "บัตรสำหรับเปิดสถานะ Midnight VIP 15 วัน" },
		identifiedDisplayName = "Midnight VIP Card [15 Days]",
		identifiedResourceName = "midnight_vip_15",
		identifiedDescriptionName = {
			"^FFD700Midnight VIP Card [15 Days]^000000\n" ..
			"^111111ใช้เพื่อเพิ่มสถานะ VIP ให้ทั้งบัญชี^000000\n" ..
			"^00AAFFระยะเวลาใช้งาน 15 วัน^000000\n" ..
			"^111111หากมี VIP อยู่แล้ว ระยะเวลาจะสะสมต่อจากเดิม^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111บัตรจะหายเมื่อระบบยืนยันเวลา VIP สำเร็จเท่านั้น^000000\n" ..
			"^111111สถานะ VIP ใช้ร่วมกันทุกตัวละครในบัญชี^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมใช้งาน | น้ำหนัก: 0^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[902246] = {
		unidentifiedDisplayName = "Midnight VIP Card [30 Days]",
		unidentifiedResourceName = "midnight_vip_30",
		unidentifiedDescriptionName = { "บัตรสำหรับเปิดสถานะ Midnight VIP 30 วัน" },
		identifiedDisplayName = "Midnight VIP Card [30 Days]",
		identifiedResourceName = "midnight_vip_30",
		identifiedDescriptionName = {
			"^FFD700Midnight VIP Card [30 Days]^000000\n" ..
			"^111111ใช้เพื่อเพิ่มสถานะ VIP ให้ทั้งบัญชี^000000\n" ..
			"^00AAFFระยะเวลาใช้งาน 30 วัน^000000\n" ..
			"^111111หากมี VIP อยู่แล้ว ระยะเวลาจะสะสมต่อจากเดิม^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111บัตรจะหายเมื่อระบบยืนยันเวลา VIP สำเร็จเท่านั้น^000000\n" ..
			"^111111สถานะ VIP ใช้ร่วมกันทุกตัวละครในบัญชี^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมใช้งาน | น้ำหนัก: 0^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[100001] = {
		unidentifiedDisplayName = "[CBT] กล่องทุนทดสอบ",
		unidentifiedResourceName = "\188\177\185\176\187\243\192\218",
		unidentifiedDescriptionName = { "กล่องทุนสำหรับทดสอบ CBT" },
		identifiedDisplayName = "[CBT] กล่องทุนทดสอบ",
		identifiedResourceName = "\188\177\185\176\187\243\192\218",
		identifiedDescriptionName = {
			"^111111เปิดเพื่อรับทุนสำหรับทดสอบ CBT^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ได้รับ 100,000,000 Zeny^000000\n" ..
			"^111111และ Coin 10,000 เหรียญ^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ห้ามแลกเปลี่ยน โยนทิ้ง หรือขาย^000000\n" ..
			"^111111ห้ามใส่รถเข็นและฝากคลัง^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมใช้งาน^000000\n" ..
			"^111111น้ำหนัก: 0^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[35022] = {
		unidentifiedDisplayName = "Costume Midnight RO Aura",
		unidentifiedResourceName = "C_Midnight_RO_Aura",
		unidentifiedDescriptionName = { "" },
		identifiedDisplayName = "Costume Midnight RO Aura",
		identifiedResourceName = "C_Midnight_RO_Aura",
		identifiedDescriptionName = {
			"^111111ตรา MIDNIGHT RO ลอยเหนือศีรษะ พร้อมแสงจันทราและประกายราตรี^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111Drop Rate +5% | EXP +5% | Max HP +400 | Max SP +200^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ห้ามแลกเปลี่ยน ซื้อขาย ส่งจดหมาย ประมูล หรือโยนลงพื้น | ฝากคลังได้^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111Costume Lower (ส่วนปาก) | น้ำหนัก 0 | เลเวล 1 | ทุกอาชีพ^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = true
	},
}

tbl_custom[902265] = {}
for key, value in pairs(tbl_custom[35022]) do
	tbl_custom[902265][key] = value
end
tbl_custom[902265].unidentifiedDisplayName = "[NFS] Costume Midnight RO Aura"
tbl_custom[902265].identifiedDisplayName = "[NFS] Costume Midnight RO Aura"























































-- Solo Leveling Shadow Monarch Hunter Rank Costumes
tbl_custom[902269] = {
	unidentifiedDisplayName = "[Hunter C] Kasaka Shadow Fang",
	unidentifiedResourceName = "kasaka_shadow_fang",
	unidentifiedDescriptionName = { "ไอเทมเกียรติยศ Hunter Rank C" },
	identifiedDisplayName = "[Hunter C] Kasaka Shadow Fang",
	identifiedResourceName = "kasaka_shadow_fang",
	identifiedDescriptionName = {
		"^FF9900[Hunter C] Kasaka Shadow Fang^000000\n" ..
		"^111111กริชเขี้ยวพิษคาซากะสีดำขลับ คมดาบอาบไอพิษสีฟ้าคราม^000000\n" ..
		"^111111รางวัลเกียรติยศสำหรับ Hunter ผู้ผ่านการประเมิน Rank C^000000\n" ..
		"^B7DFE5====================^000000\n" ..
		"^111111ประเภท : Costume^000000\n" ..
		"^111111ตำแหน่ง : ส่วนล่าง (Lower)^000000\n" ..
		"^111111น้ำหนัก : 0^000000\n" ..
		"^111111เลเวลที่ต้องการ : 1^000000\n" ..
		"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
	},
	slotCount = 0,
	ClassNum = 2850,
	costume = true
}

tbl_custom[902270] = {
	unidentifiedDisplayName = "[Hunter B] Obsidian Crown of the Monarch",
	unidentifiedResourceName = "obsidian_monarch_crown",
	unidentifiedDescriptionName = { "ไอเทมเกียรติยศ Hunter Rank B" },
	identifiedDisplayName = "[Hunter B] Obsidian Crown of the Monarch",
	identifiedResourceName = "obsidian_monarch_crown",
	identifiedDescriptionName = {
		"^FF9900[Hunter B] Obsidian Crown of the Monarch^000000\n" ..
		"^111111มงกุฎผลึกหินสีดำออบซิเดียน สลักอักขระรูนโบราณเรืองแสงสีม่วง-คราม^000000\n" ..
		"^111111รางวัลเกียรติยศสำหรับ Hunter ผู้ผ่านการประเมิน Rank B^000000\n" ..
		"^B7DFE5====================^000000\n" ..
		"^111111ประเภท : Costume^000000\n" ..
		"^111111ตำแหน่ง : ส่วนบน (Upper)^000000\n" ..
		"^111111น้ำหนัก : 0^000000\n" ..
		"^111111เลเวลที่ต้องการ : 1^000000\n" ..
		"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
	},
	slotCount = 0,
	ClassNum = 2851,
	costume = true
}

tbl_custom[902271] = {
	unidentifiedDisplayName = "[Hunter A] Monarch's Shadow Gaze",
	unidentifiedResourceName = "monarch_shadow_gaze",
	unidentifiedDescriptionName = { "ไอเทมเกียรติยศ Hunter Rank A" },
	identifiedDisplayName = "[Hunter A] Monarch's Shadow Gaze",
	identifiedResourceName = "monarch_shadow_gaze",
	identifiedDescriptionName = {
		"^FF9900[Hunter A] Monarch's Shadow Gaze^000000\n" ..
		"^111111ดวงตาเปลวไฟสีฟ้าครามสว่างวาบ พร้อมไอวิญญาณสีฟ้าลอยพริ้วจากหางตา (Animated)^000000\n" ..
		"^111111รางวัลเกียรติยศสำหรับ Hunter ผู้ผ่านการประเมิน Rank A^000000\n" ..
		"^B7DFE5====================^000000\n" ..
		"^111111ประเภท : Costume^000000\n" ..
		"^111111ตำแหน่ง : ส่วนกลาง (Middle)^000000\n" ..
		"^111111น้ำหนัก : 0^000000\n" ..
		"^111111เลเวลที่ต้องการ : 1^000000\n" ..
		"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
	},
	slotCount = 0,
	ClassNum = 2852,
	costume = true
}

tbl_custom[902272] = {
	unidentifiedDisplayName = "[Hunter S] Monarch's Shadow Aura",
	unidentifiedResourceName = "monarch_shadow_aura",
	unidentifiedDescriptionName = { "ไอเทมเกียรติยศ Hunter Rank S" },
	identifiedDisplayName = "[Hunter S] Monarch's Shadow Aura",
	identifiedResourceName = "monarch_shadow_aura",
	identifiedDescriptionName = {
		"^FF9900[Hunter S] Monarch's Shadow Aura^000000\n" ..
		"^111111ออร่าหมอกเงาแห่งจักรพรรดิสีดำพวยพุ่งขึ้นจากใต้ฝ่าเท้าพร้อมประกายเพลิงวิญญาณสีฟ้าคราม (Animated)^000000\n" ..
		"^111111รางวัลเกียรติยศสูงสุดสำหรับ Hunter ผู้ผ่านการประเมิน Rank S^000000\n" ..
		"^B7DFE5====================^000000\n" ..
		"^111111ประเภท : Costume^000000\n" ..
		"^111111ตำแหน่ง : มัฟหลัง (Garment)^000000\n" ..
		"^111111น้ำหนัก : 0^000000\n" ..
		"^111111เลเวลที่ต้องการ : 1^000000\n" ..
		"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
	},
	slotCount = 0,
	ClassNum = 0,
	costume = true
}

















tbl_custom[902273] = {
	unidentifiedDisplayName = "Newbie Pastel Poring Hat",
	unidentifiedResourceName = "pastel_poring_trio",
	unidentifiedDescriptionName = { "หมวกแก๊งโพริ่งสีม่วงพาสเทลแสนน่ารัก" },
	identifiedDisplayName = "Newbie Pastel Poring Hat",
	identifiedResourceName = "pastel_poring_trio",
	identifiedDescriptionName = {
		"^0055FF[Midnight RO - Starter Gear]^000000\n" ..
		"^111111หมวกแก๊งโพริ่งสีม่วงพาสเทลนุ่มฟู (Animated)^000000\n" ..
		"^111111โพริ่งตัวใหญ่ดุ๊กดิ๊กตรงกลาง พร้อม 2 เบบี้โพริ่งซ้ายขวา^000000\n" ..
		"^111111สลับผลัดกันกระโดดเด้งดึ๋งอย่างเป็นธรรมชาติและมีชีวิตชีวา^000000\n" ..
		"^B7DFE5====================^000000\n" ..
		"^007700MaxHP +200^000000\n" ..
		"^007700MaxSP +50^000000\n" ..
		"^007700อัตราการฟื้นฟูตามธรรมชาติ HP / SP +10%^000000\n" ..
		"^B7DFE5====================^000000\n" ..
		"^111111ประเภท : เครื่องป้องกัน (Armor)^000000\n" ..
		"^111111ตำแหน่ง : ส่วนบน (Head_Top)^000000\n" ..
		"^111111พลังป้องกัน : 3^000000\n" ..
		"^111111น้ำหนัก : 0^000000\n" ..
		"^111111เลเวลที่ต้องการ : 1^000000\n" ..
		"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000\n" ..
		"^FF3300ไอเทมผูกมัดตัวละคร ไม่สามารถแลกเปลี่ยนได้^000000"
	},
	slotCount = 0,
	ClassNum = 2853
}

-- Table for Official Overrides
-- ID 100000 exists in the client as a test item, so it must be overridden.
tbl_override = {
	[7776] = {
		unidentifiedDisplayName = "Gym Pass",
		unidentifiedResourceName = "\196\171\199\193\182\243\192\204\191\235\177\199",
		unidentifiedDescriptionName = { "Gym Pass" },
		identifiedDisplayName = "Gym Pass",
		identifiedResourceName = "\196\171\199\193\182\243\192\204\191\235\177\199",
		identifiedDescriptionName = { "^FFD700Gym Pass^000000\n^111111\227\170\233\161\209\186 NPC \189\214\161 Gym Pass \224\190\215\232\205\224\190\212\232\193\185\233\211\203\185\209\161\183\213\232\225\186\161\228\180\233 +300 \181\232\205\195\208\180\209\186\202\161\212\197^000000\n^111111\202\161\212\197\185\213\233\224\195\213\194\185\228\180\233\202\217\167\202\216\180 10 \195\208\180\209\186^000000\n^B7DFE5====================^000000\n^111111\187\195\208\224\192\183: \162\205\167\183\209\232\199\228\187 | \185\233\211\203\185\209\161: 1^000000" },
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[671] = {
		unidentifiedDisplayName = "Coin",
		unidentifiedResourceName = "\177\221\200\173",
		unidentifiedDescriptionName = { "" },
		identifiedDisplayName = "Coin",
		identifiedResourceName = "\177\221\200\173",
		identifiedDescriptionName = {
			"^111111เหรียญรางวัลพิเศษ^000000\n" ..
			"^111111หาได้จากเวลาออนไลน์^000000\n" ..
			"^111111กิจกรรม และมอนสเตอร์^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^00AAFFกดใช้ครั้งละ 10 Coin^000000\n" ..
			"^00AAFFแลกเป็น 10 Point^000000\n" ..
			"^FF7777ต้องมีอย่างน้อย 10 Coin^000000\n" ..
			"^111111Cash Shop: 10 Point ต่อ 10 Coin^000000\n" ..
			"^111111ห้ามโยนและขาย NPC^000000\n" ..
			"^111111แลกเปลี่ยนและฝากได้^000000\n" ..
			"^111111ตั้งร้านขายได้^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมใช้งาน^000000\n" ..
			"^111111น้ำหนัก: 0^000000\n" ..
			"^111111อาชีพ: ทุกอาชีพ^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[100000] = {
		unidentifiedDisplayName = "Auto Hunt",
		unidentifiedResourceName = "AI_System",
		unidentifiedDescriptionName = { "" },
		identifiedDisplayName = "Auto Hunt",
		identifiedResourceName = "AI_System",
		identifiedDescriptionName = {
			"^111111ระบบควบคุมตัวละคร^000000\n" ..
			"^111111และทำงานอัตโนมัติ^000000\n" ..
			"^111111เก็บไอเทมและใช้สกิล^000000\n" ..
			"^111111ฟื้นฟูระหว่างต่อสู้^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111คุณสมบัติไอเทม^000000\n" ..
			"^111111เปิดหน้าตั้งค่า AI^000000\n" ..
			"^111111ใช้ได้วันละ 10 ชั่วโมง^000000\n" ..
			"^111111ต่อหนึ่งบัญชี^000000\n" ..
			"^111111รีเซ็ตเวลา 00:00 น.^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ขณะ AI ทำงาน^000000\n" ..
			"^111111อัตราดรอปไอเทม^000000\n" ..
			"^111111จากมอนสเตอร์ลดลง 50%^000000\n" ..
			"^111111ห้ามโยนหรือแลกเปลี่ยน^000000\n" ..
			"^111111ห้ามขายหรือใส่รถเข็น^000000\n" ..
			"^111111ไม่สามารถฝากคลังได้^000000\n" ..
			"^111111ไอเทมไม่หายหลังใช้งาน^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111เตรียมยาและ Fly Wing^000000\n" ..
			"^111111ให้พร้อมก่อนใช้งาน^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมใช้งาน^000000\n" ..
			"^111111น้ำหนัก: 0^000000\n" ..
			"^111111เลเวลที่ต้องการ: 1^000000\n" ..
			"^111111อาชีพ: ทุกอาชีพ^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	[100002] = {
		unidentifiedDisplayName = "Midnight Token",
		unidentifiedResourceName = "midnight_token",
		unidentifiedDescriptionName = { "" },
		identifiedDisplayName = "Midnight Token",
		identifiedResourceName = "midnight_token",
		identifiedDescriptionName = {
			"^111111เหรียญรางวัลจาก Midnight Board^000000\n" ..
			"^111111ใช้แลก Costume ที่ Midnight Costume Shop^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ห้ามโยน แลกเปลี่ยน ขาย ส่งจดหมาย หรือประมูล^000000\n" ..
			"^111111ฝากคลังตัวเองได้^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมทั่วไป^000000\n" ..
			"^111111น้ำหนัก: 0^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
	-- ID 6635 exists in LuaFiles514/itemInfo.lua with the official kRO step table
	-- ProjectRO uses its own +1 through +7 table via db/pre-re/refine.yml,
	-- so the whole entry is replaced here.
	[6635] = {
		unidentifiedDisplayName = "Blacksmith Blessing",
		unidentifiedResourceName = "Blacksmith_Blessing",
		unidentifiedDescriptionName = { "" },
		identifiedDisplayName = "Blacksmith Blessing",
		identifiedResourceName = "Blacksmith_Blessing",
		identifiedDescriptionName = {
			"^111111พรจากช่างตีเหล็ก^000000\n" ..
			"^111111ใช้ป้องกันอุปกรณ์^000000\n" ..
			"^111111ระหว่างการตีบวก^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111เมื่อตีบวกล้มเหลว^000000\n" ..
			"^111111อุปกรณ์จะไม่แตก^000000\n" ..
			"^111111และไม่ถูกลดขั้น^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111จำนวนที่ต้องใช้ต่อครั้ง^000000\n" ..
			"^111111ขั้น 0 -> 1 : 1 ea^000000\n" ..
			"^111111ขั้น 1 -> 2 : 1 ea^000000\n" ..
			"^111111ขั้น 2 -> 3 : 1 ea^000000\n" ..
			"^111111ขั้น 3 -> 4 : 1 ea^000000\n" ..
			"^111111ขั้น 4 -> 5 : 1 ea^000000\n" ..
			"^111111ขั้น 5 -> 6 : 2 ea^000000\n" ..
			"^111111ขั้น 6 -> 7 : 3 ea^000000\n" ..
			"^111111ใช้ได้สูงสุดถึงการตีขึ้น +7^000000\n" ..
			"^111111ไม่รองรับการตีขึ้น +8 ถึง +10^000000\n" ..
			"^B7DFE5====================^000000\n" ..
			"^111111ประเภท: ไอเทมทั่วไป^000000\n" ..
			"^111111น้ำหนัก: 0^000000\n" ..
			"^111111ห้ามโยนทิ้ง^000000"
		},
		slotCount = 0,
		ClassNum = 0,
		costume = false
	},
}

-- BEGIN GENERATED MIDNIGHT COSTUME INTRINSIC VARIANTS
-- Generated by tools/server/build_midnight_costume_shop_variants.py.
-- These are intrinsic Item DB bonuses, not Random Options.
local midnightCostumeTemplates = {
	{ 900000, "Costume Valkyrie Feather Band", "\185\223\197\176\184\174\177\234\197\208\184\240\192\218", 300, "Upper", "0", 1, "ทุกอาชีพ" },
	{ 900056, "Costume Deviruchi Hat", "\187\245\179\162\190\199\184\182\184\240\192\218", 123, "Upper", "10", 1, "ทุกอาชีพ" },
	{ 900112, "Costume King Poring Hat", "\197\183\198\247\184\181\184\240\192\218", 905, "Upper", "10", 1, "ทุกอาชีพ" },
	{ 900168, "Costume Cherry Blossom Hat", "\186\162\178\201\184\240\192\218", 1330, "Upper", "0", 1, "ทุกอาชีพ" },
	{ 900224, "Costume Angel Wings", "\195\181\187\231\192\199\184\211\184\174\182\236", 38, "Upper", "0", 1, "ทุกอาชีพ" },
	{ 900280, "Costume Valkyrie Helm", "\185\223\197\176\184\174\197\245\177\184", 225, "Upper", "10", 1, "ทุกอาชีพ" },
	{ 900336, "Costume Angelring Hat", "\191\163\193\169\184\181\184\240\192\218", 204, "Upper", "1", 1, "ทุกอาชีพ" },
	{ 900392, "Costume Rabbit Ear Hat", "\197\228\179\162\177\205\184\240\192\218", 384, "Upper", "0", 1, "ทุกอาชีพ" },
	{ 900448, "Costume Crown of Ancient Queen", "\191\169\191\213\192\199\197\245\177\184", 164, "Upper", "0", 1, "ทุกอาชีพ" },
	{ 900504, "Costume Freya's Crown", "\199\193\183\185\192\204\190\223\192\199\197\169\182\243\191\238", 328, "Upper", "0", 1, "ทุกอาชีพ" },
	{ 900560, "Costume Sunglasses", "\188\177\177\219\183\161\189\186", 12, "Middle", "0", 1, "ทุกอาชีพ" },
	{ 900616, "Costume Black Glasses", "\176\203\192\186\187\212\197\215\190\200\176\230", 404, "Middle", "0", 1, "ทุกอาชีพ" },
	{ 900672, "Costume Heart Eyepatch", "\199\207\198\174\190\200\180\235", 779, "Middle", "0", 1, "ทุกอาชีพ" },
	{ 900728, "Costume Cool Pirate Eyepatch", "\184\218\193\248\199\216\192\251\190\200\180\235", 1097, "Middle", "10", 1, "ทุกอาชีพ" },
	{ 900784, "Costume Evil Wing Ears", "\190\199\184\182\179\175\176\179\177\205", 152, "Middle", "0", 1, "ทุกอาชีพ" },
	{ 900840, "Costume Gemini Eyes(Red)", "Gemini_RedEyes", 1654, "Middle", "0", 1, "ทุกอาชีพ" },
	{ 900896, "Costume Yellow Butterfly Wings", "\179\170\186\241\179\175\176\179\177\205", 695, "Middle", "0", 1, "ทุกอาชีพ" },
	{ 900952, "Costume Wing Angels Ears", "\195\181\187\231\179\175\176\179\177\205", 158, "Middle", "0", 1, "ทุกอาชีพ" },
	{ 901008, "Costume Poring Sunglasses", "\198\247\184\181\188\177\177\219\183\161\189\186", 954, "Middle", "0", 1, "ทุกอาชีพ" },
	{ 901064, "Costume Blinking Purple Eyes", "C_Blink_Eyes_Sakura_Princess", 2004, "Middle", "0", 1, "ทุกอาชีพ" },
	{ 901120, "Costume Fish in mouth", "\192\212\191\161\185\174\185\176\176\237\177\226", 406, "Lower", "0", 1, "ทุกอาชีพ" },
	{ 901176, "Costume Oxygen Mask", "\187\234\188\210\184\182\189\186\197\169", 90, "Lower", "0", 1, "ทุกอาชีพ" },
	{ 901232, "Costume Angry Snarl", "\186\208\179\235\192\212", 194, "Lower", "0", 1, "ทุกอาชีพ" },
	{ 901288, "Costume Romantic Leaf", "\199\174\192\217", 57, "Lower", "0", 1, "ทุกอาชีพ" },
	{ 901344, "Costume Bubble Gum in Mouth", "\192\212\191\161\185\174\199\179\188\177\178\173", 572, "Lower", "0", 1, "ทุกอาชีพ" },
	{ 901400, "Costume Flying Galapago", "\179\175\192\184\180\194\176\165\182\243\198\196\176\237", 1358, "Lower", "0", 1, "ทุกอาชีพ" },
	{ 901456, "Costume Romantic White Flower", "\199\207\190\225\178\201\192\217", 259, "Lower", "0", 1, "ทุกอาชีพ" },
	{ 901512, "Costume Cherryblossom in Mouth", "\192\212\191\161\185\171\180\194\186\162\178\201\176\161\193\246", 823, "Lower", "0", 1, "ทุกอาชีพ" },
	{ 901568, "Costume Honeynut Donut", "\192\212\191\161\185\174\179\202\198\174\181\181\179\211", 736, "Lower", "0", 1, "ทุกอาชีพ" },
	{ 901624, "Costume Heart Angel", "C_Heart_Angel_TW", 2170, "Lower", "0", 1, "ทุกอาชีพ" },
	{ 901680, "Costume Wings of Michael", "Wings_of_Michael", 24, "Garment", "0", 1, "ทุกอาชีพ" },
	{ 901736, "Costume Wings of Uriel", "\191\236\184\174\191\164\192\199\179\175\176\179", 17, "Garment", "0", 1, "ทุกอาชีพ" },
	{ 901792, "Costume Large Foxtail", "C_Big_Foxtail", 62, "Garment", "0", 1, "ทุกอาชีพ" },
	{ 901848, "Costume Cherry Blossom Wings", "C_Sakura_Wing", 83, "Garment", "0", 1, "ทุกอาชีพ" },
	{ 901904, "Costume Valkyries Wings", "C_Valkyrie_Wing", 48, "Garment", "0", 1, "ทุกอาชีพ" },
	{ 901960, "Costume Blue Wings of Fairy", "\191\228\193\164\192\199\198\196\182\245\179\175\176\179", 21, "Garment", "0", 1, "ทุกอาชีพ" },
	{ 902016, "Costume Giant Cat Bag", "GiantCatBag", 25, "Garment", "0", 1, "ทุกอาชีพ" },
	{ 902072, "Costume Backside Ribbon Bell", "Backside_Ribbon_Bell", 46, "Garment", "0", 1, "ทุกอาชีพ" },
	{ 902128, "Costume Crescent Moon", "C_Loli_Ruri_Moon", 64, "Garment", "0", 1, "ทุกอาชีพ" },
	{ 902184, "Costume Fallen Angel Wings", "\197\184\182\244\195\181\187\231\192\199\179\175\176\179", 3, "Garment", "0", 1, "ทุกอาชีพ" },
}
local midnightCostumeBonuses = {
	"EXP +1%",
	"EXP +2%",
	"EXP +3%",
	"EXP +4%",
	"EXP +5%",
	"Drop Rate +1%",
	"Drop Rate +2%",
	"Drop Rate +3%",
	"Drop Rate +4%",
	"Drop Rate +5%",
	"ASPD +1%",
	"Monster Damage +1%",
	"Monster Damage +2%",
	"Monster Damage +3%",
	"HIT +1",
	"HIT +2",
	"HIT +3",
	"Critical +1",
	"Critical +2",
	"Variable Cast -1%",
	"Variable Cast -2%",
	"Variable Cast -3%",
	"SP Consumption -1%",
	"SP Consumption -2%",
	"SP Consumption -3%",
	"ATK +1%",
	"ATK +2%",
	"ATK +3%",
	"MATK +1%",
	"MATK +2%",
	"MATK +3%",
	"Max HP +1%",
	"Max HP +2%",
	"Max HP +3%",
	"Max SP +1%",
	"Max SP +2%",
	"Max SP +3%",
	"Physical Damage Reduction +1%",
	"Physical Damage Reduction +2%",
	"Physical Damage Reduction +3%",
	"Magical Damage Reduction +1%",
	"Magical Damage Reduction +2%",
	"Magical Damage Reduction +3%",
	"HP Recovery +2%",
	"HP Recovery +3%",
	"HP Recovery +4%",
	"HP Recovery +5%",
	"SP Recovery +2%",
	"SP Recovery +3%",
	"SP Recovery +4%",
	"SP Recovery +5%",
	"All Stats +1",
	"Weight Limit +200",
	"Weight Limit +300",
	"Weight Limit +400",
	"Weight Limit +500",
}
for _, item in ipairs(midnightCostumeTemplates) do
	for bonusIndex, bonusText in ipairs(midnightCostumeBonuses) do
		tbl_custom[item[1] + bonusIndex - 1] = {
			unidentifiedDisplayName = item[2],
			unidentifiedResourceName = item[3],
			unidentifiedDescriptionName = { "" },
			identifiedDisplayName = item[2],
			identifiedResourceName = item[3],
			identifiedDescriptionName = {
				"^111111Costume จาก Midnight Costume Shop^000000\n" ..
				"^B7DFE5====================^000000\n" ..
				"^4A90E2ออฟประจำไอเทม^000000\n" ..
				"^008800" .. bonusText .. "^000000\n" ..
				"^B7DFE5====================^000000\n" ..
				"^111111ประเภท : Costume^000000\n" ..
				"^111111ตำแหน่ง : " .. item[5] .. "^000000\n" ..
				"^111111น้ำหนัก : " .. item[6] .. "^000000\n" ..
				"^111111เลเวลที่ต้องการ : " .. item[7] .. "^000000\n" ..
				"^111111อาชีพที่ใส่ได้ : " .. item[8] .. "^000000"
			},
			slotCount = 0,
			ClassNum = item[4],
			costume = true
		}
	end
end
midnightCostumeTemplates = nil
midnightCostumeBonuses = nil
-- END GENERATED MIDNIGHT COSTUME INTRINSIC VARIANTS
