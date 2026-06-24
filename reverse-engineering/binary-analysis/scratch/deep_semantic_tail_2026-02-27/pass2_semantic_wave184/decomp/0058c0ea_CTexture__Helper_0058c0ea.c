/* address: 0x0058c0ea */
/* name: CTexture__Helper_0058c0ea */
/* signature: void __fastcall CTexture__Helper_0058c0ea(void * param_1) */


void __fastcall CTexture__Helper_0058c0ea(void *param_1)

{
  int iVar1;

  iVar1 = *(int *)param_1;
  while (iVar1 != 0) {
    iVar1 = **(int **)param_1;
    OID__FreeObject_Callback(*(int **)param_1);
    *(int *)param_1 = iVar1;
  }
  return;
}
