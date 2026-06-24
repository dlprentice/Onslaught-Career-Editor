/* address: 0x0056983b */
/* name: CRT__Are3DWordsZero */
/* signature: int __cdecl CRT__Are3DWordsZero(void * param_1) */


int __cdecl CRT__Are3DWordsZero(void *param_1)

{
  int iVar1;

  iVar1 = 0;
  do {
    if (*(int *)param_1 != 0) {
      return 0;
    }
    iVar1 = iVar1 + 1;
    param_1 = (void *)((int)param_1 + 4);
  } while (iVar1 < 3);
  return 1;
}
