/* address: 0x0056eb1b */
/* name: CRT__StrDup */
/* signature: uint * __cdecl CRT__StrDup(void * param_1) */


uint * __cdecl CRT__StrDup(void *param_1)

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
