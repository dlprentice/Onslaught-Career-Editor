/* address: 0x005b35b0 */
/* name: CFastVB__Unk_005b35b0 */
/* signature: int __stdcall CFastVB__Unk_005b35b0(int param_1) */


int CFastVB__Unk_005b35b0(int param_1)

{
  undefined1 *puVar1;
  char *pcVar2;
  int *in_EAX;
  int iVar3;
  int *piVar4;

  iVar3 = CFastVB__Helper_005b3370(0x7f);
  if (iVar3 == 0) {
    return 0;
  }
  puVar1 = (undefined1 *)*in_EAX;
  *puVar1 = 0xff;
  *in_EAX = (int)(puVar1 + 1);
  iVar3 = in_EAX[1];
  in_EAX[2] = 0;
  in_EAX[3] = 0;
  in_EAX[1] = iVar3 + -1;
  if (iVar3 + -1 == 0) {
    piVar4 = *(int **)(in_EAX[8] + 0x18);
    iVar3 = (*(code *)piVar4[3])(in_EAX[8]);
    if (iVar3 == 0) {
      return 0;
    }
    iVar3 = piVar4[1];
    *in_EAX = *piVar4;
    in_EAX[1] = iVar3;
  }
  pcVar2 = (char *)*in_EAX;
  *pcVar2 = (char)param_1 + -0x30;
  *in_EAX = (int)(pcVar2 + 1);
  piVar4 = in_EAX + 1;
  *piVar4 = *piVar4 + -1;
  if (*piVar4 == 0) {
    piVar4 = *(int **)(in_EAX[8] + 0x18);
    iVar3 = (*(code *)piVar4[3])(in_EAX[8]);
    if (iVar3 == 0) {
      return 0;
    }
    iVar3 = piVar4[1];
    *in_EAX = *piVar4;
    in_EAX[1] = iVar3;
  }
  iVar3 = 0;
  if (0 < *(int *)(in_EAX[8] + 0xfc)) {
    piVar4 = in_EAX + 4;
    do {
      *piVar4 = 0;
      iVar3 = iVar3 + 1;
      piVar4 = piVar4 + 1;
    } while (iVar3 < *(int *)(in_EAX[8] + 0xfc));
  }
  return 1;
}
