/* address: 0x00574abb */
/* name: CDXTexture__RepeatCallbackN */
/* signature: void __stdcall CDXTexture__RepeatCallbackN(int param_1, int param_2, int param_3, void * param_4) */


void CDXTexture__RepeatCallbackN(int param_1,int param_2,int param_3,void *param_4)

{
  if (-1 < param_3 + -1) {
    do {
      (*param_4)();
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}
