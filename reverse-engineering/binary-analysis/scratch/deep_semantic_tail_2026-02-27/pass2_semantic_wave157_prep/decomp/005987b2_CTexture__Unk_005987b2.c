/* address: 0x005987b2 */
/* name: CTexture__Unk_005987b2 */
/* signature: int __stdcall CTexture__Unk_005987b2(int param_1, int param_2) */


int CTexture__Unk_005987b2(int param_1,int param_2)

{
  int *piVar1;

  if (param_1 != 0) {
    piVar1 = &param_1;
    do {
      piVar1 = (int *)(*piVar1 + 0xc);
    } while (*piVar1 != 0);
    *piVar1 = param_2;
    param_2 = param_1;
  }
  return param_2;
}
