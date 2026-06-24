/* address: 0x00573cc0 */
/* name: CTexture__Unk_00573cc0 */
/* signature: void __stdcall CTexture__Unk_00573cc0(void * param_1) */


void CTexture__Unk_00573cc0(void *param_1)

{
  int *piVar1;

  if (param_1 != DAT_009d0c44) {
    do {
      CTexture__Unk_00573cc0(*(void **)((int)param_1 + 8));
      piVar1 = *(int **)param_1;
      OID__FreeObject_Callback(param_1);
      param_1 = piVar1;
    } while (piVar1 != DAT_009d0c44);
  }
  return;
}
