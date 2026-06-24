/* address: 0x00504d30 */
/* name: CVBufTexture__IsTransitionAllowedByState */
/* signature: bool __fastcall CVBufTexture__IsTransitionAllowedByState(int param_1) */


bool __fastcall CVBufTexture__IsTransitionAllowedByState(int param_1)

{
  int iVar1;

  iVar1 = CVBufTexture__Helper_004fd760(param_1);
  if (iVar1 != 0) {
    return true;
  }
  return *(int *)(param_1 + 0x168) == 0;
}
