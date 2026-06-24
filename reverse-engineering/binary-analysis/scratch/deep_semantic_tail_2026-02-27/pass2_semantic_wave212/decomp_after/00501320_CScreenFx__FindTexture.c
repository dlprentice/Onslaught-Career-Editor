/* address: 0x00501320 */
/* name: CScreenFx__FindTexture */
/* signature: void __cdecl CScreenFx__FindTexture(void * param_1, int param_2) */


void __cdecl CScreenFx__FindTexture(void *param_1,int param_2)

{
  int *piVar1;

  piVar1 = CTexture__FindTexture(param_1,0,0,param_2,1,1);
  CHud__Helper_004f27e0((int)(piVar1 + 2));
  CVBufTexture__GetOrCreate(piVar1,0);
  return;
}
