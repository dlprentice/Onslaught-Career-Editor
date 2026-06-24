/* address: 0x00459c10 */
/* name: CFEPMultiplayerStart__SubObj8848__ButtonPressed */
/* signature: void CFEPMultiplayerStart__SubObj8848__ButtonPressed(void * this, int button) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CFEPMultiplayerStart__SubObj8848__ButtonPressed(void *this,int button)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int in_ECX;
  double dVar5;
  float fVar6;

  iVar1 = *(int *)(in_ECX + 0x3468);
  iVar2 = *(int *)(in_ECX + 0x346c);
  iVar3 = *(int *)(in_ECX + 0xcc + (iVar2 + iVar1 * 6) * 4);
  switch(this) {
  case (void *)0x2a:
    *(int *)(in_ECX + 0x346c) = iVar2 + 1;
    iVar4 = *(int *)(in_ECX + 4 + iVar1 * 4);
    if (iVar4 <= iVar2 + 1) {
      *(int *)(in_ECX + 0x346c) = iVar4 + -1;
    }
    CFrontEnd__PlaySound(0);
    break;
  case (void *)0x2b:
    *(int *)(in_ECX + 0x346c) = iVar2 + -1;
    if (iVar2 + -1 < 0) {
      *(undefined4 *)(in_ECX + 0x346c) = 0;
    }
    CFrontEnd__PlaySound(0);
    break;
  case (void *)0x2c:
    CFrontEnd__SetPage(&DAT_0089d758,5,0x1e);
    CFrontEnd__PlaySound(1);
    DAT_0089d94c = *(undefined4 *)
                    (in_ECX + 0xcc + (*(int *)(in_ECX + 0x346c) + *(int *)(in_ECX + 0x3468) * 6) * 4
                    );
    break;
  default:
    goto switchD_00459c5e_caseD_2d;
  case (void *)0x2e:
    CFrontEnd__PlaySound(2);
    CFrontEnd__SetPage(&DAT_0089d758,0xc,0);
    break;
  case (void *)0x36:
    *(int *)(in_ECX + 0x3468) = iVar1 + -1;
    if (iVar1 + -1 < 0) {
      *(undefined4 *)(in_ECX + 0x3468) = 0;
    }
    CFrontEnd__PlaySound(0);
    break;
  case (void *)0x37:
    *(int *)(in_ECX + 0x3468) = iVar1 + 1;
    if (*(int *)(in_ECX + 0x345c) <= iVar1 + 1) {
      *(int *)(in_ECX + 0x3468) = *(int *)(in_ECX + 0x345c) + -1;
    }
    CFrontEnd__PlaySound(0);
  }
  *(undefined4 *)(in_ECX + 0x347c) = 0;
switchD_00459c5e_caseD_2d:
  iVar4 = *(int *)(in_ECX + 4 + *(int *)(in_ECX + 0x3468) * 4);
  if (iVar4 <= *(int *)(in_ECX + 0x346c)) {
    *(int *)(in_ECX + 0x346c) = iVar4 + -1;
  }
  dVar5 = CTexture__Unk_0055dfe7((double)(_DAT_005db520 / (float)(*(int *)(in_ECX + 0x345c) + -1)));
  fVar6 = (float)*(int *)(in_ECX + 0x3468);
  *(float *)(in_ECX + 0x3464) = fVar6 * _DAT_005db020 - fVar6 * (float)dVar5;
  if ((*(int *)(in_ECX + 0x3468) != iVar1) || (*(int *)(in_ECX + 0x346c) != iVar2)) {
    fVar6 = PLATFORM__GetSysTimeFloat();
    *(float *)(in_ECX + 0x3474) = fVar6;
  }
  if (*(int *)(in_ECX + 0xcc + (*(int *)(in_ECX + 0x346c) + *(int *)(in_ECX + 0x3468) * 6) * 4) /
      100 != iVar3 / 100) {
    fVar6 = PLATFORM__GetSysTimeFloat();
    *(float *)(in_ECX + 0x3470) = fVar6;
  }
  return;
}
