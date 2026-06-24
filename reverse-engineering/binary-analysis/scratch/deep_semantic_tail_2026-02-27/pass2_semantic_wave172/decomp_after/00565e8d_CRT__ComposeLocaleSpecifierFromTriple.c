/* address: 0x00565e8d */
/* name: CRT__ComposeLocaleSpecifierFromTriple */
/* signature: void __cdecl CRT__ComposeLocaleSpecifierFromTriple(int param_1, int param_2) */


void __cdecl CRT__ComposeLocaleSpecifierFromTriple(int param_1,int param_2)

{
  CRT__StrCpyAligned((void *)param_1,(void *)param_2);
  if (*(char *)(param_2 + 0x40) != '\0') {
    CRT__StrCatVarArgs(param_1,2);
  }
  if (*(char *)(param_2 + 0x80) != '\0') {
    CRT__StrCatVarArgs(param_1,2);
  }
  return;
}
