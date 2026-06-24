/* address: 0x0058c107 */
/* name: CTexture__Helper_0058c107 */
/* signature: void __thiscall CTexture__Helper_0058c107(void * this, void * param_1, int param_2) */


void __thiscall CTexture__Helper_0058c107(void *this,void *param_1,int param_2)

{
  undefined4 *extraout_EAX;

  OID__AllocObject_DefaultTag_00662b2c((int)param_1 + 4);
  if (extraout_EAX != (undefined4 *)0x0) {
    *extraout_EAX = *(undefined4 *)this;
    *(undefined4 **)this = extraout_EAX;
  }
  return;
}
