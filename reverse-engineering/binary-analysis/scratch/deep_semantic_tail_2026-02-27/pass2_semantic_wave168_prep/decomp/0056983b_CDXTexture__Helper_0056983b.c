/* address: 0x0056983b */
/* name: CDXTexture__Helper_0056983b */
/* signature: int __cdecl CDXTexture__Helper_0056983b(void * param_1) */


int __cdecl CDXTexture__Helper_0056983b(void *param_1)

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
