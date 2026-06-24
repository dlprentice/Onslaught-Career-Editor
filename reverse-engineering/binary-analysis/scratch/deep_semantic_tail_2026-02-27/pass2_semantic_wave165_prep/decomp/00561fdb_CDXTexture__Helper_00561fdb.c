/* address: 0x00561fdb */
/* name: CDXTexture__Helper_00561fdb */
/* signature: void __cdecl CDXTexture__Helper_00561fdb(void * param_1, int param_2, void * param_3, void * param_4) */


void __cdecl CDXTexture__Helper_00561fdb(void *param_1,int param_2,void *param_3,void *param_4)

{
  char cVar1;

  do {
    if (param_2 < 1) {
      return;
    }
    param_2 = param_2 + -1;
    cVar1 = *(char *)param_1;
    param_1 = (void *)((int)param_1 + 1);
    CDXTexture__Helper_00561f75((int)cVar1,param_3,param_4);
  } while (*(int *)param_4 != -1);
  return;
}
