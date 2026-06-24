/* address: 0x005952e0 */
/* name: CTexture__SetDecodeTableEpoch */
/* signature: void __stdcall CTexture__SetDecodeTableEpoch(int param_1, int param_2) */


void CTexture__SetDecodeTableEpoch(int param_1,int param_2)

{
  int *piVar1;
  int iVar2;

  if (*(int *)(param_1 + 0x48) != 0) {
    *(int *)(*(int *)(param_1 + 0x48) + 0x80) = param_2;
  }
  if (*(int *)(param_1 + 0x4c) != 0) {
    *(int *)(*(int *)(param_1 + 0x4c) + 0x80) = param_2;
  }
  if (*(int *)(param_1 + 0x50) != 0) {
    *(int *)(*(int *)(param_1 + 0x50) + 0x80) = param_2;
  }
  if (*(int *)(param_1 + 0x54) != 0) {
    *(int *)(*(int *)(param_1 + 0x54) + 0x80) = param_2;
  }
  piVar1 = (int *)(param_1 + 0x68);
  iVar2 = 4;
  do {
    if (piVar1[-4] != 0) {
      *(int *)(piVar1[-4] + 0x114) = param_2;
    }
    if (*piVar1 != 0) {
      *(int *)(*piVar1 + 0x114) = param_2;
    }
    piVar1 = piVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}
