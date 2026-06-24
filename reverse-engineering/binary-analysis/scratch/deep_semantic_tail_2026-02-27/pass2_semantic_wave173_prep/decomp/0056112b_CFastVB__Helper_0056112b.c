/* address: 0x0056112b */
/* name: CFastVB__Helper_0056112b */
/* signature: void __cdecl CFastVB__Helper_0056112b(void * param_1, int param_2) */


void __cdecl CFastVB__Helper_0056112b(void *param_1,int param_2)

{
  size_t sVar1;

  if (param_2 != 0) {
    sVar1 = _strlen(param_1);
    CRT__MemMoveOverlapSafe((void *)((int)param_1 + param_2),param_1,sVar1 + 1);
  }
  return;
}
