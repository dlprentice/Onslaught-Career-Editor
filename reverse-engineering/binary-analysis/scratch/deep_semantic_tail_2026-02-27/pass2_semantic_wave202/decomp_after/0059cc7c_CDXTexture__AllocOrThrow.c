/* address: 0x0059cc7c */
/* name: CDXTexture__AllocOrThrow */
/* signature: void * __stdcall CDXTexture__AllocOrThrow(void * param_1, int param_2) */


void * CDXTexture__AllocOrThrow(void *param_1,int param_2)

{
  void *pvVar1;

  if ((param_1 == (void *)0x0) || (param_2 == 0)) {
    pvVar1 = (void *)0x0;
  }
  else {
    pvVar1 = _malloc(param_2);
    if (pvVar1 == (void *)0x0) {
      CDXTexture__ThrowDecodeError(param_1,0x5f39ac);
    }
  }
  return pvVar1;
}
