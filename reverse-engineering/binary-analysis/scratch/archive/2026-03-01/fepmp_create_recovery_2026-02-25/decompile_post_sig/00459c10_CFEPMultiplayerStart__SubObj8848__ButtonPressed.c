/* address: 0x00459c10 */
/* name: CFEPMultiplayerStart__SubObj8848__ButtonPressed */
/* signature: undefined CFEPMultiplayerStart__SubObj8848__ButtonPressed(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CFEPMultiplayerStart__SubObj8848__ButtonPressed(int param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  double dVar5;
  float fVar6;

  iVar1 = *(int *)(param_1 + 0x3468);
  iVar2 = *(int *)(param_1 + 0x346c);
  iVar3 = *(int *)(param_1 + 0xcc + (iVar2 + iVar1 * 6) * 4);
  switch(param_2) {
  case 0x2a:
    *(int *)(param_1 + 0x346c) = iVar2 + 1;
    iVar4 = *(int *)(param_1 + 4 + iVar1 * 4);
    if (iVar4 <= iVar2 + 1) {
      *(int *)(param_1 + 0x346c) = iVar4 + -1;
    }
    CFrontEnd__PlaySound(0);
    break;
  case 0x2b:
    *(int *)(param_1 + 0x346c) = iVar2 + -1;
    if (iVar2 + -1 < 0) {
      *(undefined4 *)(param_1 + 0x346c) = 0;
    }
    CFrontEnd__PlaySound(0);
    break;
  case 0x2c:
    CFrontEnd__SetPage(&DAT_0089d758,5,0x1e);
    CFrontEnd__PlaySound(1);
    DAT_0089d94c = *(undefined4 *)
                    (param_1 + 0xcc +
                    (*(int *)(param_1 + 0x346c) + *(int *)(param_1 + 0x3468) * 6) * 4);
    break;
  default:
    goto switchD_00459c5e_caseD_2d;
  case 0x2e:
    CFrontEnd__PlaySound(2);
    CFrontEnd__SetPage(&DAT_0089d758,0xc,0);
    break;
  case 0x36:
    *(int *)(param_1 + 0x3468) = iVar1 + -1;
    if (iVar1 + -1 < 0) {
      *(undefined4 *)(param_1 + 0x3468) = 0;
    }
    CFrontEnd__PlaySound(0);
    break;
  case 0x37:
    *(int *)(param_1 + 0x3468) = iVar1 + 1;
    if (*(int *)(param_1 + 0x345c) <= iVar1 + 1) {
      *(int *)(param_1 + 0x3468) = *(int *)(param_1 + 0x345c) + -1;
    }
    CFrontEnd__PlaySound(0);
  }
  *(undefined4 *)(param_1 + 0x347c) = 0;
switchD_00459c5e_caseD_2d:
  iVar4 = *(int *)(param_1 + 4 + *(int *)(param_1 + 0x3468) * 4);
  if (iVar4 <= *(int *)(param_1 + 0x346c)) {
    *(int *)(param_1 + 0x346c) = iVar4 + -1;
  }
  dVar5 = CTexture__Unk_0055dfe7((double)(_DAT_005db520 / (float)(*(int *)(param_1 + 0x345c) + -1)))
  ;
  fVar6 = (float)*(int *)(param_1 + 0x3468);
  *(float *)(param_1 + 0x3464) = fVar6 * _DAT_005db020 - fVar6 * (float)dVar5;
  if ((*(int *)(param_1 + 0x3468) != iVar1) || (*(int *)(param_1 + 0x346c) != iVar2)) {
    fVar6 = PLATFORM__GetSysTimeFloat();
    *(float *)(param_1 + 0x3474) = fVar6;
  }
  if (*(int *)(param_1 + 0xcc + (*(int *)(param_1 + 0x346c) + *(int *)(param_1 + 0x3468) * 6) * 4) /
      100 != iVar3 / 100) {
    fVar6 = PLATFORM__GetSysTimeFloat();
    *(float *)(param_1 + 0x3470) = fVar6;
  }
  return;
}
