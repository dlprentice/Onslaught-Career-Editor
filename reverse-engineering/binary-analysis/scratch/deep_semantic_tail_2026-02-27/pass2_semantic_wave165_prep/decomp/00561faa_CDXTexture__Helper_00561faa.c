/* address: 0x00561faa */
/* name: CDXTexture__Helper_00561faa */
/* signature: void __cdecl CDXTexture__Helper_00561faa(uint param_1, int param_2, void * param_3, void * param_4) */


void __cdecl CDXTexture__Helper_00561faa(uint param_1,int param_2,void *param_3,void *param_4)

{
  do {
    if (param_2 < 1) {
      return;
    }
    param_2 = param_2 + -1;
    CDXTexture__Helper_00561f75(param_1,param_3,param_4);
  } while (*(int *)param_4 != -1);
  return;
}
