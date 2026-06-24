/* address: 0x0048f320 */
/* name: CLandscapeVB__VFunc_01_0048f320 */
/* signature: int __fastcall CLandscapeVB__VFunc_01_0048f320(int param_1) */


int __fastcall CLandscapeVB__VFunc_01_0048f320(int param_1)

{
  int iVar1;

  iVar1 = CVBuffer__Restore();
  if (*(int *)(param_1 + 0x40) != 0) {
    CUnitAI__Unk_0048f210(param_1);
  }
  return iVar1;
}
