/* address: 0x0058948d */
/* name: CTexture__Helper_0058948d */
/* signature: void * __thiscall CTexture__Helper_0058948d(void * this, void * param_1, int param_2) */


void * __thiscall CTexture__Helper_0058948d(void *this,void *param_1,int param_2)

{
  CDXTexture__Unk_00589438((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
