/* address: 0x004599a0 */
/* name: CFEPMultiplayerStart__SubObj8848__Init */
/* signature: undefined CFEPMultiplayerStart__SubObj8848__Init(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 __fastcall CFEPMultiplayerStart__SubObj8848__Init(int param_1)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  double dVar5;
  float fVar6;

  iVar4 = 0;
  *(undefined4 *)(param_1 + 0x3468) = 0;
  *(undefined4 *)(param_1 + 0x346c) = 0;
  piVar3 = (int *)(param_1 + 0xcc);
  do {
    iVar1 = 0;
    piVar2 = piVar3;
    do {
      if (*piVar2 == DAT_0089d94c) {
        *(int *)(param_1 + 0x3468) = iVar4;
        *(int *)(param_1 + 0x346c) = iVar1;
        goto LAB_004599f0;
      }
      iVar1 = iVar1 + 1;
      piVar2 = piVar2 + 1;
    } while (iVar1 < 6);
    iVar4 = iVar4 + 1;
    piVar3 = piVar3 + 6;
  } while (iVar4 < 0x32);
LAB_004599f0:
  dVar5 = CTexture__Unk_0055dfe7((double)(_DAT_005db520 / (float)(*(int *)(param_1 + 0x345c) + -1)))
  ;
  fVar6 = (float)*(int *)(param_1 + 0x3468) * _DAT_005db020 -
          (float)*(int *)(param_1 + 0x3468) * (float)dVar5;
  *(float *)(param_1 + 0x3464) = fVar6;
  *(float *)(param_1 + 0x3460) = fVar6;
  fVar6 = PLATFORM__GetSysTimeFloat();
  *(float *)(param_1 + 0x3470) = fVar6;
  fVar6 = PLATFORM__GetSysTimeFloat();
  *(float *)(param_1 + 0x3474) = fVar6;
  return 1;
}
