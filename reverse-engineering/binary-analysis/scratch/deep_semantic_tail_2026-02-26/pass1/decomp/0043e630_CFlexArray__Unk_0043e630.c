/* address: 0x0043e630 */
/* name: CFlexArray__Unk_0043e630 */
/* signature: void __cdecl CFlexArray__Unk_0043e630(int param_1, int param_2) */


void __cdecl CFlexArray__Unk_0043e630(int param_1,int param_2)

{
  int iVar1;

  iVar1 = param_2;
  if (0 < param_2) {
    do {
      DXMemBuffer__ReadBytes(&param_2,1);
      iVar1 = iVar1 + -1;
    } while (iVar1 != 0);
  }
  return;
}
