/* address: 0x00453ad0 */
/* name: CControllerDefinition__VFunc_04_00453ad0 */
/* signature: undefined CControllerDefinition__VFunc_04_00453ad0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CControllerDefinition__VFunc_04_00453ad0(int param_1,float param_2,float param_3,int param_4)

{
  float fVar1;
  int *piVar2;
  uint uVar3;
  char *pcVar4;
  int *piVar5;
  short sVar6;
  int iVar7;
  float *pfVar8;
  float *pfVar9;
  undefined4 *puVar10;
  float *pfVar11;
  int key_or_value;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 fVar12;
  int iStack_20;
  float afStack_18 [5];
  float fStack_4;

  fVar1 = param_3 + _DAT_005d85d8;
  iStack_20 = 0;
  do {
    ControlsUI__RenderBindingsList
              (iStack_20,((float)iStack_20 - _DAT_005d8568) * _DAT_005db490 + param_2,fVar1,param_4)
    ;
    iStack_20 = iStack_20 + 1;
  } while (iStack_20 < 3);
  if (*(int *)(param_1 + 0x2c) == 0) {
    piVar2 = CTexture__FindTexture(s_FrontEnd_v2_FE_Arrow_tga_006290f4,0,0,1,0,1);
    *(int **)(param_1 + 0x2c) = piVar2;
  }
  if (0 < *(int *)(param_1 + 0x20)) {
    PLATFORM__GetSysTimeFloat();
    CDXTexture__Unk_0055e3ea();
    if (extraout_ST0 < (float10)_DAT_005d8bd8) {
      CDXSurf__RenderSurface
                (param_2,param_3 + _DAT_005d85d4,0,*(undefined4 *)(param_1 + 0x2c),0xffffffff,
                 0x3f800000,0x3f800000,4,0,0x3f800000,0xbfc90fdb);
    }
    if ((param_4 != 0) &&
       (uVar3 = CVBufTexture__Unk_00523cc0
                          (param_2 - _DAT_005d8bc0,fVar1 - _DAT_005d8be8,param_2 + _DAT_005d8bc0,
                           param_3 + _DAT_005db484), (char)uVar3 != '\0')) {
      CFrontEnd__PlaySound(0);
      *(int *)(param_1 + 0x20) = *(int *)(param_1 + 0x20) + -1;
    }
  }
  if ((float)*(int *)(param_1 + 0x20) < _DAT_005d8df8) {
    PLATFORM__GetSysTimeFloat();
    CDXTexture__Unk_0055e3ea();
    if (extraout_ST0_00 < (float10)_DAT_005d8bd8) {
      CDXSurf__RenderSurface
                (param_2,(param_3 + _DAT_005db480) - _DAT_005d85cc,0,*(undefined4 *)(param_1 + 0x2c)
                 ,0xffffffff,0x3f800000,0x3f800000,4,0,0x3f800000,0x3fc90fdb);
    }
    if ((param_4 != 0) &&
       (uVar3 = CVBufTexture__Unk_00523cc0
                          (param_2 - _DAT_005d8bc0,(param_3 + _DAT_005db480) - _DAT_005db478,
                           param_2 + _DAT_005d8bc0,param_3 + _DAT_005db47c), (char)uVar3 != '\0')) {
      CFrontEnd__PlaySound(0);
      *(int *)(param_1 + 0x20) = *(int *)(param_1 + 0x20) + 1;
    }
  }
  if ((g_ControlRemapActive != '\0') || (key_or_value = 0, DAT_00888ff8 < 1)) {
    return;
  }
  pfVar9 = (float *)&DAT_0067780c;
  piVar2 = &DAT_00888f94;
  do {
    iVar7 = 0;
    pcVar4 = (char *)(piVar2[4] + 0x30);
    do {
      if ((*pcVar4 == '\0') && (*(char *)(*piVar2 + 0x30 + iVar7) != '\0')) {
        sVar6 = (short)iVar7;
        g_ControlRemapBindingType = 1;
        g_ControlRemapVkScanPacked._2_2_ = sVar6;
        if (DAT_008892dc != -1) {
          puVar10 = &DAT_008892dc;
          do {
            if (*(char *)(puVar10 + -1) != '\0') {
              piVar2 = puVar10 + 1;
              iVar7 = 2;
              do {
                if ((*piVar2 == key_or_value) && ((short)piVar2[2] == sVar6)) {
                  switch(piVar2[1]) {
                  default:
                    *piVar2 = -1;
                    break;
                  case 4:
                  case 5:
                  case 6:
                  case 7:
                  case 8:
                  case 9:
                  case 10:
                  case 0xb:
                  case 0xc:
                  case 0xd:
                  case 0xe:
                  case 0xf:
                  case 0x10:
                  case 0x11:
                    break;
                  }
                }
                piVar2 = piVar2 + 3;
                iVar7 = iVar7 + -1;
              } while (iVar7 != 0);
            }
            piVar2 = puVar10 + 8;
            puVar10 = puVar10 + 8;
          } while (*piVar2 != -1);
        }
        Controls__DispatchRemap(g_ControlRemapActionCode,key_or_value,&LAB_004540c0);
        Controls__ApplyPreset(0);
        goto LAB_00453ee9;
      }
      iVar7 = iVar7 + 1;
      pcVar4 = pcVar4 + 1;
    } while (iVar7 < 0x80);
    piVar5 = DAT_008a9564;
    if (DAT_008a9564 == (int *)0x0) {
      piVar5 = CGame__GetController(&DAT_008a9a98,0);
    }
    (**(code **)(*piVar5 + 0x24))(key_or_value);
    (**(code **)(*piVar5 + 0x28))(key_or_value);
    (**(code **)(*piVar5 + 0x2c))(key_or_value);
    (**(code **)(*piVar5 + 0x30))(key_or_value);
    (**(code **)(*piVar5 + 0x34))(key_or_value);
    fVar12 = (float10)(**(code **)(*piVar5 + 0x38))(key_or_value);
    fStack_4 = (float)fVar12;
    iVar7 = -1;
    pfVar8 = afStack_18 + 1;
    pfVar11 = pfVar9;
    do {
      sVar6 = (short)iVar7;
      if (pfVar8[-1] - pfVar11[-1] < _DAT_005d8c8c) {
        g_ControlRemapBindingType = 5;
        g_ControlRemapVkScanPacked._2_2_ = sVar6;
LAB_00453ee1:
        Controls__RemapKey(g_ControlRemapActionCode,key_or_value);
LAB_00453ee9:
        g_ControlRemapActive = 1;
        PLATFORM__SetKeySink((void *)0x0);
        return;
      }
      if (_DAT_005d8bb8 < pfVar8[-1] - pfVar11[-1]) {
        g_ControlRemapBindingType = 4;
        g_ControlRemapVkScanPacked._2_2_ = sVar6;
        goto LAB_00453ee1;
      }
      if (*pfVar8 - *pfVar11 < _DAT_005d8c8c) {
        g_ControlRemapBindingType = 5;
        g_ControlRemapVkScanPacked._2_2_ = sVar6 + -1;
        goto LAB_00453ee1;
      }
      if (_DAT_005d8bb8 < *pfVar8 - *pfVar11) {
        g_ControlRemapBindingType = 4;
        g_ControlRemapVkScanPacked._2_2_ = sVar6 + -1;
        goto LAB_00453ee1;
      }
      iVar7 = iVar7 + -2;
      pfVar8 = pfVar8 + 2;
      pfVar11 = pfVar11 + 2;
    } while (-6 < iVar7);
    key_or_value = key_or_value + 1;
    piVar2 = piVar2 + 1;
    pfVar9 = pfVar9 + 6;
    if (DAT_00888ff8 <= key_or_value) {
      return;
    }
  } while( true );
}
