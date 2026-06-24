/* address: 0x00568189 */
/* name: CRT__MapCodePageToLocaleId_00568189 */
/* signature: int __cdecl CRT__MapCodePageToLocaleId_00568189(int param_1) */


int __cdecl CRT__MapCodePageToLocaleId_00568189(int param_1)

{
  if (param_1 == 0x3a4) {
    return 0x411;
  }
  if (param_1 == 0x3a8) {
    return 0x804;
  }
  if (param_1 == 0x3b5) {
    return 0x412;
  }
  if (param_1 != 0x3b6) {
    return 0;
  }
  return 0x404;
}
