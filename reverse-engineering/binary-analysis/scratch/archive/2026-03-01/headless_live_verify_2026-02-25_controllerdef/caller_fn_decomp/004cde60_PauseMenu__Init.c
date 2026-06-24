/* address: 0x004cde60 */
/* name: PauseMenu__Init */
/* signature: void __thiscall PauseMenu__Init(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Builds pause menu entries. God-mode option is gated by IsCheatActive(3) and reads
   g_bGodModeEnabled (CAREER+0x2494 / file 0x2496) as toggle state; per-player mIsGod persistence
   not present in Steam save region (invert-Y settings live at 0x249E+). */

void __thiscall PauseMenu__Init(void *this)

{
  void *this_00;
  int iVar1;
  short *psVar2;
  void *pvVar3;
  undefined4 *puVar4;
  wchar_t *pwVar5;
  void *this_01;
  undefined4 extraout_EAX;
  undefined4 *puVar6;
  int *piVar7;
  undefined4 unaff_EBX;
  char in_stack_00000004;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 local_20;
  undefined8 local_14;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d458f;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  CMonitor__ctor(this);
  *(undefined ***)this = &PTR_CFrontEndPage__ActiveNotification_NoOp_005dc72c;
  this_00 = (void *)((int)this + 0x14);
  local_4 = 0;
  *(undefined4 *)((int)this + 0x10) = 0;
  CSPtrSet__Init(this_00);
  *(undefined4 *)((int)this + 0x24) = 0;
  *(undefined4 *)((int)this + 0x30) = 0xbf800000;
  *(undefined ***)this = &PTR_LAB_005de6fc;
  local_4._0_1_ = 1;
  DAT_0082b4e8 = in_stack_00000004;
  local_20 = 0x43960000;
  if (in_stack_00000004 == '\0') {
    local_20 = 0x43700000;
  }
  iVar1 = OID__AllocObject(0x30,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x539);
  local_14 = CONCAT44(local_14._4_4_,iVar1);
  local_4._0_1_ = 2;
  if (iVar1 == 0) {
    pvVar3 = (void *)0x0;
  }
  else {
    uVar11 = 0xb0000000;
    uVar10 = 0;
    uVar9 = 0x43a00000;
    uVar8 = local_20;
    psVar2 = CText__GetStringById(&g_Text,0x130ed7);
    pvVar3 = (void *)CMenuItemRange__Init(psVar2,uVar9,uVar8,uVar10,uVar11);
  }
  local_4 = CONCAT31(local_4._1_3_,1);
  if (in_stack_00000004 == '\0') {
    puVar4 = (undefined4 *)
             OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x53d);
    if (puVar4 == (undefined4 *)0x0) {
      puVar4 = (undefined4 *)0x0;
    }
    else {
      puVar4[1] = 2;
      puVar4[2] = 0x41d6e9;
      puVar4[3] = 0;
      puVar4[4] = 1;
      puVar4[5] = 0xffd6d6d6;
      puVar4[6] = 0;
      *puVar4 = &PTR_LAB_005db440;
    }
    CMenuItemRange__AddItem(puVar4);
    puVar4 = (undefined4 *)
             OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x53e);
    if (puVar4 == (undefined4 *)0x0) {
      puVar4 = (undefined4 *)0x0;
    }
    else {
      puVar4[1] = 2;
      puVar4[2] = 0x1f08cea;
      puVar4[3] = 0;
      puVar4[4] = 1;
      puVar4[5] = 0xffd6d6d6;
      puVar4[6] = 0;
      *puVar4 = &PTR_LAB_005db440;
    }
    CMenuItemRange__AddItem(puVar4);
    puVar4 = (undefined4 *)
             OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x53f);
    if (puVar4 == (undefined4 *)0x0) {
      CMenuItemRange__AddItem(0);
    }
    else {
      puVar4[1] = 2;
      puVar4[2] = 0x3fc4f9;
      puVar4[3] = 0;
      puVar4[4] = 1;
      puVar4[5] = 0xffd6d6d6;
      puVar4[6] = 0;
      *puVar4 = &PTR_LAB_005db440;
      CMenuItemRange__AddItem(puVar4);
    }
  }
  puVar4 = (undefined4 *)
           OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x542);
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4[2] = 0;
    puVar4[1] = 3;
    puVar4[3] = 0;
    puVar4[4] = 1;
    puVar4[5] = 0xffd6d6d6;
    puVar4[6] = 3;
    *puVar4 = &PTR_LAB_005db440;
  }
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x543);
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4[1] = 3;
    puVar4[2] = 0;
    puVar4[3] = 0;
    puVar4[4] = 1;
    puVar4[5] = 0xffd6d6d6;
    puVar4[6] = 1;
    *puVar4 = &PTR_LAB_005db440;
  }
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x544);
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4[1] = 3;
    puVar4[2] = 0;
    puVar4[3] = 0;
    puVar4[4] = 1;
    puVar4[5] = 0xffd6d6d6;
    puVar4[6] = 2;
    *puVar4 = &PTR_LAB_005db440;
  }
  CMenuItemRange__AddItem(puVar4);
  if (in_stack_00000004 == '\0') {
    puVar4 = (undefined4 *)
             OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x54e);
    if (puVar4 == (undefined4 *)0x0) {
      puVar4 = (undefined4 *)0x0;
    }
    else {
      puVar4[1] = 2;
      puVar4[2] = 0xcada9;
      puVar4[3] = 0;
      puVar4[4] = 1;
      puVar4[5] = 0xffd6d6d6;
      puVar4[6] = 0;
      *puVar4 = &PTR_LAB_005db440;
    }
    CMenuItemRange__AddItem(puVar4);
    puVar4 = (undefined4 *)
             OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x54f);
    if (puVar4 != (undefined4 *)0x0) {
      puVar4[1] = 2;
      puVar4[2] = 0x7a211;
      goto LAB_004ce1cf;
    }
LAB_004ce1e7:
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4 = (undefined4 *)
             OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x549);
    if (puVar4 == (undefined4 *)0x0) goto LAB_004ce1e7;
    puVar4[1] = 1;
    puVar4[2] = &LAB_00437a3e;
LAB_004ce1cf:
    puVar4[3] = 0;
    puVar4[4] = 1;
    puVar4[5] = 0xffd6d6d6;
    puVar4[6] = 0;
    *puVar4 = &PTR_LAB_005db440;
  }
  CMenuItemRange__AddItem(puVar4);
  CSPtrSet__AddToTail(this_00,pvVar3);
  iVar1 = OID__AllocObject(0x30,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x558);
  local_4._0_1_ = 3;
  if (iVar1 == 0) {
    pvVar3 = (void *)0x0;
  }
  else {
    uVar11 = 0xb0000000;
    uVar10 = 0;
    uVar9 = 0x43a00000;
    uVar8 = local_20;
    pwVar5 = Localization__GetStringById(3);
    pvVar3 = (void *)CMenuItemRange__Init(pwVar5,uVar9,uVar8,uVar10,uVar11);
  }
  local_4._0_1_ = 1;
  puVar4 = (undefined4 *)
           OID__AllocObject(0x38,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x55d);
  local_4._0_1_ = 4;
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    CMenuItem__InitWithIcon(0x4e,3,0,0,0x14,1);
    *puVar4 = &PTR_CMouseSensitivityMenuItem__VFunc_00_004cf030_005de6b8;
    local_14 = (longlong)ROUND(g_MouseSensitivity * _DAT_005d8608 + _DAT_005d85ec);
    puVar4[9] = (int)local_14 + -1;
    puVar4[10] = (int)local_14 + -1;
  }
  local_4._0_1_ = 1;
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x562);
  local_4._0_1_ = 5;
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__Init(0xef,3,0);
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de66c;
  }
  local_4 = CONCAT31(local_4._1_3_,1);
  CMenuItemRange__AddItem(puVar4);
  iVar1 = IsCheatActive(&DAT_008a1374,3);
  if (iVar1 != 0) {
    if (g_bGodModeEnabled == 1) {
      puVar4 = (undefined4 *)
               OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x568);
      if (puVar4 == (undefined4 *)0x0) goto LAB_004ce3a4;
      puVar4[1] = 3;
      puVar4[2] = 0x148fe9;
LAB_004ce38c:
      puVar4[3] = 0;
      puVar4[4] = 1;
      puVar4[5] = 0xffd6d6d6;
      puVar4[6] = 0;
      *puVar4 = &PTR_LAB_005db440;
    }
    else {
      puVar4 = (undefined4 *)
               OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x56c);
      if (puVar4 != (undefined4 *)0x0) {
        puVar4[1] = 3;
        puVar4[2] = 0x226f16;
        goto LAB_004ce38c;
      }
LAB_004ce3a4:
      puVar4 = (undefined4 *)0x0;
    }
    CMenuItemRange__AddItem(puVar4);
  }
  this_01 = (void *)OID__AllocObject(0x30,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x570);
  local_4._0_1_ = 6;
  if (this_01 == (void *)0x0) {
    uVar8 = 0;
  }
  else {
    CControllerDefinition__InitDefaults(this_01);
    uVar8 = extraout_EAX;
  }
  local_4._0_1_ = 1;
  CMenuItemRange__AddItem(uVar8);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x20,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x572);
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4[1] = 3;
    puVar4[2] = 0;
    puVar4[3] = 0;
    puVar4[4] = 1;
    puVar4[5] = 0xffd6d6d6;
    puVar4[6] = 0x5d;
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de630;
    puVar4[7] = 0;
  }
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x20,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x573);
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4[1] = 3;
    puVar4[2] = 0;
    puVar4[3] = 0;
    puVar4[4] = 1;
    puVar4[5] = 0xffd6d6d6;
    puVar4[6] = 0x5d;
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de630;
    puVar4[7] = 1;
  }
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x20,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x574);
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4[1] = 3;
    puVar4[2] = 0;
    puVar4[3] = 0;
    puVar4[4] = 1;
    puVar4[5] = 0xffd6d6d6;
    puVar4[6] = 0x5d;
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de630;
    puVar4[7] = 2;
  }
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x20,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x575);
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4[2] = 0;
    puVar4[1] = 3;
    puVar4[3] = 0;
    puVar4[4] = 1;
    puVar4[5] = 0xffd6d6d6;
    puVar4[6] = 0x5d;
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de630;
    puVar4[7] = 3;
  }
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x577);
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4[1] = 3;
    puVar4[2] = 0x6f9da;
    puVar4[3] = 0;
    puVar4[4] = 1;
    puVar4[5] = 0xffd6d6d6;
    puVar4[6] = 0;
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de5f4;
  }
  CMenuItemRange__AddItem(puVar4);
  CSPtrSet__AddToTail(this_00,pvVar3);
  iVar1 = OID__AllocObject(0x30,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x57d);
  local_4._0_1_ = 7;
  if (iVar1 == 0) {
    pvVar3 = (void *)0x0;
  }
  else {
    uVar10 = 0xb0000000;
    uVar9 = 0;
    uVar8 = 0x43a00000;
    pwVar5 = Localization__GetStringById(2);
    pvVar3 = (void *)CMenuItemRange__Init(pwVar5,uVar8,local_20,uVar9,uVar10);
  }
  local_4._0_1_ = 1;
  puVar4 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x580);
  local_4._0_1_ = 8;
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__InitVariant(0xf7,3,1);
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de5a8;
  }
  local_4._0_1_ = 1;
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x58,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x583);
  local_4._0_1_ = 9;
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__Init(0xdf,3,0);
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de55c;
    puVar4[10] = 0;
    puVar4[0xb] = 0;
    puVar4[0xc] = 0;
    puVar4[0xd] = 0;
    puVar4[0xe] = 0;
    puVar4[0xf] = 0;
    puVar4[0x10] = 0;
    puVar4[0x11] = 0;
    puVar4[0x12] = 0;
    if (DAT_0089c07c == 0) {
      puVar4[0x13] = 0;
    }
    else {
      puVar4[0x13] = 1;
    }
    if (DAT_008aa96c < 4) {
      puVar4[0x14] = 0;
      puVar4[0x15] = 0;
    }
    else if (DAT_008aa96c < 5) {
      puVar4[0x14] = 0;
      puVar4[0x15] = 4;
    }
    else {
      puVar4[0x14] = 4;
      puVar4[0x15] = 5;
    }
  }
  local_4._0_1_ = 1;
  CMenuItemRange__AddItem(puVar4);
  puVar6 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x587);
  local_4._0_1_ = 10;
  if (puVar6 == (undefined4 *)0x0) {
    puVar6 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__Init(0x13,3,1);
    *puVar6 = &PTR_VFuncSlot_00_004d0490_005de510;
  }
  local_4._0_1_ = 1;
  puVar4[10] = puVar6;
  CMenuItemRange__AddItem(puVar6);
  piVar7 = (int *)OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x588);
  local_4._0_1_ = 0xb;
  if (piVar7 == (int *)0x0) {
    piVar7 = (int *)0x0;
  }
  else {
    CMenuItemDropdown__Init(0xe,3,0);
    *piVar7 = (int)&PTR_VFuncSlot_00_004d0490_005de4c4;
  }
  DAT_0082b48c = piVar7;
  puVar4[0xb] = piVar7;
  local_4._0_1_ = 1;
  CMenuItemRange__AddItem(DAT_0082b48c);
  piVar7 = (int *)OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x589);
  local_4._0_1_ = 0xc;
  if (piVar7 == (int *)0x0) {
    piVar7 = (int *)0x0;
  }
  else {
    CMenuItemDropdown__Init(0xf,3,0);
    *piVar7 = (int)&PTR_VFuncSlot_00_004d0490_005de478;
  }
  DAT_0082b488 = piVar7;
  puVar4[0xc] = piVar7;
  local_4._0_1_ = 1;
  CMenuItemRange__AddItem(DAT_0082b488);
  puVar6 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x58a);
  local_4._0_1_ = 0xd;
  if (puVar6 == (undefined4 *)0x0) {
    puVar6 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__InitVariant(0x26,3,0);
    *puVar6 = &PTR_VFuncSlot_00_004d0490_005de42c;
  }
  local_4._0_1_ = 1;
  puVar4[0xd] = puVar6;
  CMenuItemRange__AddItem(puVar6);
  puVar6 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x58d);
  local_4._0_1_ = 0xe;
  if (puVar6 == (undefined4 *)0x0) {
    puVar6 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__Init(0xde,3,1);
    *puVar6 = &PTR_VFuncSlot_00_004d0490_005de3e0;
  }
  local_4._0_1_ = 1;
  CMenuItemRange__AddItem(puVar6);
  if (DAT_0089c0ac != 0) {
    puVar6 = (undefined4 *)
             OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x593);
    local_4._0_1_ = 0xf;
    if (puVar6 == (undefined4 *)0x0) {
      puVar6 = (undefined4 *)0x0;
    }
    else {
      CMenuItemDropdown__Init(0xeb,3,0);
      *puVar6 = &PTR_VFuncSlot_00_004d0490_005de394;
    }
    local_4._0_1_ = 1;
    CMenuItemRange__AddItem(puVar6);
  }
  puVar6 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x596);
  local_4._0_1_ = 0x10;
  if (puVar6 == (undefined4 *)0x0) {
    puVar6 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__InitVariant(0x14,3,1);
    *puVar6 = &PTR_VFuncSlot_00_004d0490_005de348;
  }
  local_4._0_1_ = 1;
  puVar4[0xe] = puVar6;
  CMenuItemRange__AddItem(puVar6);
  puVar6 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x597);
  local_4._0_1_ = 0x11;
  if (puVar6 == (undefined4 *)0x0) {
    puVar6 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__Init(0x15,3,0);
    *puVar6 = &PTR_VFuncSlot_00_004d0490_005de2fc;
  }
  local_4._0_1_ = 1;
  puVar4[0xf] = puVar6;
  CMenuItemRange__AddItem(puVar6);
  puVar6 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x598);
  local_4._0_1_ = 0x12;
  if (puVar6 == (undefined4 *)0x0) {
    puVar6 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__Init(0x16,3,1);
    *puVar6 = &PTR_VFuncSlot_00_004d0490_005de2b0;
  }
  local_4._0_1_ = 1;
  puVar4[0x10] = puVar6;
  CMenuItemRange__AddItem(puVar6);
  puVar6 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x599);
  local_4._0_1_ = 0x13;
  if (puVar6 == (undefined4 *)0x0) {
    puVar6 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__Init(0x1d,3,1);
    *puVar6 = &PTR_VFuncSlot_00_004d0490_005de260;
  }
  local_4._0_1_ = 1;
  puVar4[0x11] = puVar6;
  CMenuItemRange__AddItem(puVar6);
  puVar6 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x59a);
  local_4._0_1_ = 0x14;
  if (puVar6 == (undefined4 *)0x0) {
    puVar6 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__Init(0xd3,3,1);
    *puVar6 = &PTR_VFuncSlot_00_004d0490_005de214;
  }
  local_4._0_1_ = 1;
  puVar4[0x12] = puVar6;
  CMenuItemRange__AddItem(puVar6);
  iVar1 = OID__AllocObject(0x20,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x59c);
  local_4._0_1_ = 0x15;
  if (iVar1 == 0) {
    uVar8 = 0;
  }
  else {
    uVar8 = CMenuItemSlider__Init(pvVar3);
  }
  local_4 = CONCAT31(local_4._1_3_,1);
  CMenuItemRange__AddItem(uVar8);
  iVar1 = *DAT_0082b48c;
  uVar8 = (**(code **)(iVar1 + 0x3c))();
  (**(code **)(iVar1 + 0x38))(uVar8);
  iVar1 = CRTMesh__GetQualityLevel();
  if (iVar1 == 0) {
    uVar8 = 0;
    iVar1 = *DAT_0082b488;
  }
  else {
    if (iVar1 == 1) {
      (**(code **)(*DAT_0082b488 + 0x38))(1);
      goto LAB_004ceb09;
    }
    if (iVar1 != 2) goto LAB_004ceb09;
    uVar8 = 2;
    iVar1 = *DAT_0082b488;
  }
  (**(code **)(iVar1 + 0x38))(uVar8);
LAB_004ceb09:
  puVar4 = (undefined4 *)
           OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x5a1);
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4[1] = 3;
    puVar4[2] = 0x6f9da;
    puVar4[3] = 0;
    puVar4[4] = 1;
    puVar4[5] = 0xffd6d6d6;
    puVar4[6] = 0;
    *puVar4 = &PTR_LAB_005db440;
  }
  CMenuItemRange__AddItem(puVar4);
  CSPtrSet__AddToTail((void *)((int)this + 0x28),pvVar3);
  iVar1 = OID__AllocObject(0x30,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x5a8);
  puStack_8._0_1_ = 0x16;
  if (iVar1 == 0) {
    pvVar3 = (void *)0x0;
  }
  else {
    uVar10 = 0xb0000000;
    uVar9 = 0;
    uVar8 = 0x43a00000;
    pwVar5 = Localization__GetStringById(1);
    pvVar3 = (void *)CMenuItemRange__Init(pwVar5,uVar8,unaff_EBX,uVar9,uVar10);
  }
  puStack_8._0_1_ = 1;
  iVar1 = OID__AllocObject(0x38,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x5aa);
  puStack_8._0_1_ = 0x17;
  if (iVar1 == 0) {
    uVar8 = 0;
  }
  else {
    uVar8 = CMenuItem__Init(0x9d5a3f,3,CAREER_mSoundVolume,this_00,10,1);
  }
  puStack_8._0_1_ = 1;
  CMenuItemRange__AddItem(uVar8);
  iVar1 = OID__AllocObject(0x38,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x5ab);
  puStack_8._0_1_ = 0x18;
  if (iVar1 == 0) {
    uVar8 = 0;
  }
  else {
    uVar8 = CMenuItem__Init(&DAT_00939ef4,3,CAREER_mMusicVolume,this_00,10,1);
  }
  puStack_8._0_1_ = 1;
  CMenuItemRange__AddItem(uVar8);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x5ac);
  puStack_8._0_1_ = 0x19;
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__InitVariant(4,3,0);
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de1c8;
  }
  puStack_8._0_1_ = 1;
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x5ad);
  puStack_8._0_1_ = 0x1a;
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__InitVariant(7,3,1);
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de17c;
  }
  puStack_8._0_1_ = 1;
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x5ae);
  puStack_8._0_1_ = 0x1b;
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__Init(0xd8,3,1);
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de130;
  }
  puStack_8._0_1_ = 1;
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x5b1);
  puStack_8._0_1_ = 0x1c;
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__Init(9,3,1);
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de0e4;
  }
  puStack_8._0_1_ = 1;
  CMenuItemRange__AddItem(puVar4);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x28,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x5b3);
  puStack_8._0_1_ = 0x1d;
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    CMenuItemDropdown__Init(10,3,1);
    *puVar4 = &PTR_VFuncSlot_00_004d0490_005de098;
  }
  puStack_8._0_1_ = 1;
  CMenuItemRange__AddItem(puVar4);
  iVar1 = OID__AllocObject(0x20,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x5b5);
  puStack_8._0_1_ = 0x1e;
  if (iVar1 == 0) {
    uVar8 = 0;
  }
  else {
    uVar8 = CMenuItemSlider__Init(pvVar3);
  }
  puStack_8 = (undefined1 *)CONCAT31(puStack_8._1_3_,1);
  CMenuItemRange__AddItem(uVar8);
  puVar4 = (undefined4 *)
           OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x5b6);
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4[1] = 3;
    puVar4[2] = 0x6f9da;
    puVar4[3] = 0;
    puVar4[4] = 1;
    puVar4[5] = 0xffd6d6d6;
    puVar4[6] = 0;
    *puVar4 = &PTR_LAB_005db440;
  }
  CMenuItemRange__AddItem(puVar4);
  CSPtrSet__AddToTail((void *)((int)this + 0x28),pvVar3);
  *(undefined4 *)((int)this + 0x54) = 0;
  *(undefined4 *)((int)this + 0x58) = 0;
  DAT_0082b490 = 0;
  *(undefined4 *)((int)this + 0x4c) = 0;
  *(undefined4 *)((int)this + 0x1c) = 0;
  *(undefined4 *)((int)this + 0x50) = 0;
  *(undefined4 *)((int)this + 0x5c) = 0;
  *(undefined4 *)((int)this + 0x48) = 0;
  ExceptionList = local_14._4_4_;
  return;
}
