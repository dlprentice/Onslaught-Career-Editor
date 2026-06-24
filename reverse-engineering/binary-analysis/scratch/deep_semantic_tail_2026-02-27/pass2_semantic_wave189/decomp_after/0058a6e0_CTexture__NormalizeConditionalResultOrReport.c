/* address: 0x0058a6e0 */
/* name: CTexture__NormalizeConditionalResultOrReport */
/* signature: int __thiscall CTexture__NormalizeConditionalResultOrReport(void * this, int param_1, int param_2) */


int __thiscall CTexture__NormalizeConditionalResultOrReport(void *this,int param_1,int param_2)

{
  if (param_1 == 0) {
    if (*(int *)((int)this + 0x2c) == 0) {
      CTexture__Helper_0058c893((void *)((int)this + 4),(int)this + 0x60,0,0x5ea504);
      *(undefined4 *)((int)this + 0x2c) = 1;
    }
    param_1 = 0;
  }
  return param_1;
}
