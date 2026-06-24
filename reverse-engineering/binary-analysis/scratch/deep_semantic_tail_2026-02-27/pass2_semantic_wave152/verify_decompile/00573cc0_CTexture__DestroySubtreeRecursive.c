/* address: 0x00573cc0 */
/* name: CTexture__DestroySubtreeRecursive */
/* signature: void __stdcall CTexture__DestroySubtreeRecursive(void * param_1) */


void CTexture__DestroySubtreeRecursive(void *param_1)

{
  int *piVar1;

  if (param_1 != DAT_009d0c44) {
    do {
      CTexture__DestroySubtreeRecursive(*(void **)((int)param_1 + 8));
      piVar1 = *(int **)param_1;
      OID__FreeObject_Callback(param_1);
      param_1 = piVar1;
    } while (piVar1 != DAT_009d0c44);
  }
  return;
}
