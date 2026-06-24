/* address: 0x004599a0 */
/* name: CFEPMultiplayerStart__SubObj8848__Init */
/* signature: int CFEPMultiplayerStart__SubObj8848__Init(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFEPMultiplayerStart__SubObj8848__Init(void *this)

{
  int iVar1;
  int in_ECX;
  int *piVar2;
  int *piVar3;
  int iVar4;
  double dVar5;
  float fVar6;

  iVar4 = 0;
  *(undefined4 *)(in_ECX + 0x3468) = 0;
  *(undefined4 *)(in_ECX + 0x346c) = 0;
  piVar3 = (int *)(in_ECX + 0xcc);
  do {
    iVar1 = 0;
    piVar2 = piVar3;
    do {
      if (*piVar2 == DAT_0089d94c) {
        *(int *)(in_ECX + 0x3468) = iVar4;
        *(int *)(in_ECX + 0x346c) = iVar1;
        goto LAB_004599f0;
      }
      iVar1 = iVar1 + 1;
      piVar2 = piVar2 + 1;
    } while (iVar1 < 6);
    iVar4 = iVar4 + 1;
    piVar3 = piVar3 + 6;
  } while (iVar4 < 0x32);
LAB_004599f0:
  dVar5 = CTexture__Unk_0055dfe7((double)(_DAT_005db520 / (float)(*(int *)(in_ECX + 0x345c) + -1)));
  fVar6 = (float)*(int *)(in_ECX + 0x3468) * _DAT_005db020 -
          (float)*(int *)(in_ECX + 0x3468) * (float)dVar5;
  *(float *)(in_ECX + 0x3464) = fVar6;
  *(float *)(in_ECX + 0x3460) = fVar6;
  fVar6 = PLATFORM__GetSysTimeFloat();
  *(float *)(in_ECX + 0x3470) = fVar6;
  fVar6 = PLATFORM__GetSysTimeFloat();
  *(float *)(in_ECX + 0x3474) = fVar6;
  return 1;
}
