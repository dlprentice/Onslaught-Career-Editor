/* address: 0x0058c149 */
/* name: CTexture__TokenList_ClearAndFreeBuffers_0058c149 */
/* signature: void __fastcall CTexture__TokenList_ClearAndFreeBuffers_0058c149(void * param_1) */


void __fastcall CTexture__TokenList_ClearAndFreeBuffers_0058c149(void *param_1)

{
  int iVar1;

  iVar1 = *(int *)param_1;
  while (iVar1 != 0) {
    iVar1 = **(int **)param_1;
    OID__FreeObject_Callback(*(int **)param_1);
    *(int *)param_1 = iVar1;
  }
  OID__FreeObject_Callback(*(void **)((int)param_1 + 0x18));
  OID__FreeObject_Callback(*(void **)((int)param_1 + 0x1c));
  return;
}
