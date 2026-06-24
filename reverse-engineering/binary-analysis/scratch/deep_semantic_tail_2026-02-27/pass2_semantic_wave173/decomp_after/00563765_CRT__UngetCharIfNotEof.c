/* address: 0x00563765 */
/* name: CRT__UngetCharIfNotEof */
/* signature: void __cdecl CRT__UngetCharIfNotEof(int param_1, int param_2) */


void __cdecl CRT__UngetCharIfNotEof(int param_1,int param_2)

{
  if (param_1 != -1) {
    CRT__UngetCharToStream(param_1,(void *)param_2);
  }
  return;
}
