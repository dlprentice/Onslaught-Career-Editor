/* address: 0x00501320 */
/* name: CEngine__Unk_00501320 */
/* signature: void __cdecl CEngine__Unk_00501320(void * param_1, int param_2) */


void __cdecl CEngine__Unk_00501320(void *param_1,int param_2)

{
  int *piVar1;

  piVar1 = CTexture__FindTexture(param_1,0,0,param_2,1,1);
  CUnit__Unk_004f27e0((int)(piVar1 + 2));
  CVBufTexture__GetOrCreate(piVar1,0);
  return;
}
