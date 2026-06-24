/* address: 0x0059879e */
/* name: CFastVB__Helper_0059879e */
/* signature: int __stdcall CFastVB__Helper_0059879e(void * param_1) */


int CFastVB__Helper_0059879e(void *param_1)

{
  int iVar1;

  if (param_1 == (void *)0x0) {
    iVar1 = 0;
  }
  else {
    iVar1 = (**(code **)(*(int *)param_1 + 8))();
  }
  return iVar1;
}
