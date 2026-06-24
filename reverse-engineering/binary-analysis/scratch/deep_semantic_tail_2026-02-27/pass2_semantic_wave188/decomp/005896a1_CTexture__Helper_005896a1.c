/* address: 0x005896a1 */
/* name: CTexture__Helper_005896a1 */
/* signature: void * __thiscall CTexture__Helper_005896a1(void * this, void * param_1, int param_2) */


void * __thiscall CTexture__Helper_005896a1(void *this,void *param_1,int param_2)

{
  CTexture__FreeIncludeFileChainRecursive((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
