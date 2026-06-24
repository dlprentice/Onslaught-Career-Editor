/* address: 0x0059879e */
/* name: CDXTexture__InvokeNodeScoreOrZero */
/* signature: int __stdcall CDXTexture__InvokeNodeScoreOrZero(void * param_1) */


int CDXTexture__InvokeNodeScoreOrZero(void *param_1)

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
