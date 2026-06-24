/* address: 0x0056eb1b */
/* name: CDXTexture__Helper_0056eb1b */
/* signature: uint * __cdecl CDXTexture__Helper_0056eb1b(void * param_1) */


uint * __cdecl CDXTexture__Helper_0056eb1b(void *param_1)

{
  size_t sVar1;
  void *pvVar2;
  uint *puVar3;

  if (param_1 != (void *)0x0) {
    sVar1 = _strlen(param_1);
    pvVar2 = _malloc(sVar1 + 1);
    if (pvVar2 != (void *)0x0) {
      puVar3 = CRT__StrCpyAligned(pvVar2,param_1);
      return puVar3;
    }
  }
  return (uint *)0x0;
}
