/* address: 0x004662a0 */
/* name: CFrontEnd__Init */
/* signature: int __thiscall CFrontEnd__Init(void * this, int arg2, int arg3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CFrontEnd__Init(void *this,int arg2,int arg3)

{
  int iVar1;
  uint uVar2;
  void *pvVar3;
  uint uVar4;
  undefined4 *puVar5;
  int *piVar6;
  char *unaff_EDI;
  int *piVar7;
  bool bVar8;
  float fVar9;
  float fVar10;
  int local_24;
  char local_20 [20];
  void *local_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d2749;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CConsole__SetLoading(&DAT_00663498,'\x01',1);
  if (arg3 == 0) {
    fVar10 = 25.0;
    fVar9 = 0.0;
  }
  else {
    fVar10 = 62.5;
    fVar9 = 50.0;
  }
  CConsole__SetLoadingRange(&DAT_00663498,fVar9,fVar10);
  if (DAT_00662f40 != 0) {
    CSoundManager__ReloadLanguageSampleBank(&DAT_00896988);
  }
  CEventManager__Init(&EVENT_MANAGER);
  CCareer__Update();
  if (arg3 == 0) {
    fVar10 = 80.0;
    fVar9 = 25.0;
  }
  else {
    fVar10 = 90.0;
    fVar9 = 62.5;
  }
  CConsole__SetLoadingRange(&DAT_00663498,fVar9,fVar10);
  iVar1 = CFrontEnd__LoadSharedResources(&DAT_0089d760);
  if (iVar1 == 0) {
    ExceptionList = local_c;
    return 0;
  }
  iVar1 = CFrontEndPage__Init_ReturnTrue();
  if (iVar1 == 0) {
    ExceptionList = local_c;
    return 0;
  }
  if (arg3 == 0) {
    fVar10 = 90.0;
    fVar9 = 80.0;
  }
  else {
    fVar10 = 95.0;
    fVar9 = 90.0;
  }
  CConsole__SetLoadingRange(&DAT_00663498,fVar9,fVar10);
  iVar1 = CDXFrontEndVideo__SetDefaultSize(&DAT_0089d91c);
  if (iVar1 == 0) {
    ExceptionList = local_c;
    return 0;
  }
  DebugTrace(unaff_EDI);
  CFrontEnd__InitPageStateDefaults(&DAT_00675688);
  if (arg3 == 0) {
    fVar9 = 90.0;
  }
  else {
    fVar9 = 95.0;
  }
  CConsole__SetLoadingRange(&DAT_00663498,fVar9,100.0);
  piVar6 = (int *)((int)this + 0x214);
  piVar7 = piVar6;
  for (iVar1 = 0x18; iVar1 != 0; iVar1 = iVar1 + -1) {
    *piVar7 = (int)this + 0xbe04;
    piVar7 = piVar7 + 1;
  }
  *piVar6 = (int)this + 0x278;
  *(int *)((int)this + 0x218) = (int)this + 0x29c;
  *(int *)((int)this + 0x21c) = (int)this + 0x2b0;
  *(int *)((int)this + 0x220) = (int)this + 700;
  *(int *)((int)this + 0x224) = (int)this + 0x2ec;
  *(int *)((int)this + 0x228) = (int)this + 0x324;
  *(int *)((int)this + 0x22c) = (int)this + 0x338;
  *(int *)((int)this + 0x230) = (int)this + 0x360;
  *(int *)((int)this + 0x234) = (int)this + 0x37dc;
  *(int *)((int)this + 0x238) = (int)this + 0x39b8;
  *(int *)((int)this + 0x23c) = (int)this + 0x39d0;
  *(int *)((int)this + 0x240) = (int)this + 0x3c1c;
  *(int *)((int)this + 0x244) = (int)this + 0x4034;
  *(int *)((int)this + 0x254) = (int)this + 0x4050;
  *(int *)((int)this + 0x250) = (int)this + 0x40b8;
  *(int *)((int)this + 600) = (int)this + 0x40ec;
  *(int *)((int)this + 0x25c) = (int)this + 0x4118;
  *(int *)((int)this + 0x260) = (int)this + 0x4124;
  *(int *)((int)this + 0x248) = (int)this + 0x413c;
  *(int *)((int)this + 0x24c) = (int)this + 0x4834;
  *(int *)((int)this + 0x264) = (int)this + 0x8848;
  *(int *)((int)this + 0x268) = (int)this + 0xbcc8;
  *(int *)((int)this + 0x26c) = (int)this + 0xbde0;
  *(int *)((int)this + 0x270) = (int)this + 0xbe04;
  uVar4 = 1;
  local_24 = 0;
  do {
    sprintf(local_20,s_FEP__d____00629e18);
    DebugTrace(local_20);
    uVar2 = (*(code *)**(undefined4 **)*piVar6)();
    uVar4 = uVar4 & uVar2;
    DebugTrace(s_done__00629e10);
    CConsole__SetLoadingFraction(&DAT_00663498,(float)local_24 * _DAT_005dbb44);
    local_24 = local_24 + 1;
    piVar6 = piVar6 + 1;
  } while (local_24 < 0x18);
  if (uVar4 == 0) {
    ExceptionList = local_c;
    return 0;
  }
  DAT_008a9ab4 = 1;
  iVar1 = 0;
  puVar5 = (undefined4 *)((int)this + 0xbe0c);
  do {
    pvVar3 = (void *)OID__AllocObject(0x178,0x27,s_C__dev_ONSLAUGHT2_FrontEnd_cpp_00629df0,0xb3);
    uStack_4 = 0;
    if (pvVar3 == (void *)0x0) {
      pvVar3 = (void *)0x0;
    }
    else {
      pvVar3 = CController__ctor(pvVar3,this,iVar1,1);
    }
    *puVar5 = pvVar3;
    iVar1 = iVar1 + 1;
    puVar5 = puVar5 + 1;
    uStack_4 = 0xffffffff;
  } while (iVar1 < 2);
  PlatformInput__ResetKeyStateTables();
  *(undefined4 *)((int)this + 0xbe18) = 0;
  *(undefined4 *)((int)this + 0xbe14) = 0xfffffffe;
  *(undefined4 *)((int)this + 0xbe20) = 0xc2c80000;
  DAT_008a9aac = 0;
  if (DAT_0066304c != -1) {
    *(undefined4 *)((int)this + 0x1f8) = 0x17;
    CFrontEnd__SetPage(this,0,0);
    DAT_008a9580 = 1;
    DAT_008a9584 = 1;
    CFEPMultiplayerStart__SubObj39B8__QueuePageId((void *)((int)this + 0x39b8),DAT_0066304c);
    goto LAB_00466799;
  }
  if ((*(int *)((int)this + 0xbe1c) == 0) && (arg2 != 1)) {
    if (arg2 != 2) {
      iVar1 = *(int *)((int)this + 500);
      if ((iVar1 < 0x385) || (0x389 < iVar1)) {
        if ((iVar1 < 0x352) || (0x36f < iVar1)) {
          if (DAT_0083d448 == 0) {
            if ((((*(int *)((int)this + 0xbe2c) != 2) && (DAT_0083d454 == 0)) &&
                (g_bDevModeEnabled == 0)) && (g_bAllCheatsEnabled == '\0')) {
              DAT_008a9580 = 1;
              *(undefined4 *)((int)this + 0x1f8) = 0x17;
              CFrontEnd__SetPage(this,0xb,0);
              *(undefined4 *)((int)this + 0xbf34) = 6;
              *(undefined4 *)((int)this + 0xbf38) = 0x32;
              goto LAB_00466799;
            }
          }
          else if (DAT_006630cc != 0) {
            *(undefined4 *)((int)this + 0x1f8) = 0xc;
            goto LAB_00466799;
          }
          *(undefined4 *)((int)this + 0x1f8) = 6;
        }
        else {
          *(undefined4 *)((int)this + 0x1f8) = 0x10;
        }
      }
      else if (((*(int *)((int)this + 0xbe2c) == 2) || (DAT_0083d454 != 0)) ||
              ((g_bDevModeEnabled != 0 || (g_bAllCheatsEnabled != '\0')))) {
        *(undefined4 *)((int)this + 0x1f8) = 8;
      }
      else {
        DAT_008a9580 = 1;
        *(undefined4 *)((int)this + 0x1f8) = 0x17;
        CFrontEnd__SetPage(this,0xb,0);
        *(undefined4 *)((int)this + 0xbf34) = 8;
        *(undefined4 *)((int)this + 0xbf38) = 0x32;
      }
      goto LAB_00466799;
    }
    *(undefined4 *)((int)this + 0x1f8) = 0x17;
    iVar1 = 0;
  }
  else {
    *(undefined4 *)((int)this + 0xbe1c) = 0;
    bVar8 = DAT_00662dd0 == 0;
    *(undefined4 *)((int)this + 0x1f8) = 0x17;
    if ((bVar8) || ((DAT_0083d448 != 0 || (DAT_008a9ab4 == 0)))) {
      iVar1 = 0xc;
    }
    else {
      iVar1 = 0;
    }
  }
  CFrontEnd__SetPage(this,iVar1,0);
LAB_00466799:
  if (*(int *)((int)this + 0x1f8) == -1) {
    (**(code **)(**(int **)((int)this + *(int *)((int)this + 0x200) * 4 + 0x214) + 0x18))(2);
  }
  else {
    (**(code **)(**(int **)((int)this + *(int *)((int)this + 0x1f8) * 4 + 0x214) + 0x18))(2);
    (**(code **)(**(int **)((int)this + *(int *)((int)this + 0x1f8) * 4 + 0x214) + 0x1c))(2);
  }
  *(undefined4 *)((int)this + 500) = 100;
  uVar4 = 0;
  pvVar3 = (void *)((int)this + 0xbf40);
  do {
    CText__Ctor(pvVar3);
    CText__Init(pvVar3,uVar4);
    uVar4 = uVar4 + 1;
    pvVar3 = (void *)((int)pvVar3 + 0x30);
  } while ((int)uVar4 < 5);
  if (arg3 == 0) {
    fVar9 = 90.0;
  }
  else {
    fVar9 = 95.0;
  }
  CConsole__SetLoadingRange(&DAT_00663498,fVar9,100.0);
  CConsole__SetLoading(&DAT_00663498,'\0',1);
  if (DAT_00662dcc != 0) {
    CMusic__PlayTrackByType(&DAT_00889a48,0,0);
  }
  ExceptionList = local_c;
  return 1;
}
