/* address: 0x00565d9c */
/* name: CRT__StrCatVarArgs */
/* signature: void __cdecl CRT__StrCatVarArgs(int param_1, int param_2) */


void __cdecl CRT__StrCatVarArgs(int param_1,int param_2)

{
  int *piVar1;
  int *piVar2;
  int iVar3;

  if (0 < param_2) {
    piVar2 = &param_2;
    iVar3 = param_2;
    do {
      piVar1 = piVar2 + 1;
      piVar2 = piVar2 + 1;
      CRT__StrCatAligned((void *)param_1,(void *)*piVar1);
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
  }
  return;
}
