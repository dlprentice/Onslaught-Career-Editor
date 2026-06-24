/* address: 0x0058939b */
/* name: CTexture__Helper_0058939b */
/* signature: void * __thiscall CTexture__Helper_0058939b(void * this, void * param_1, int param_2) */


void * __thiscall CTexture__Helper_0058939b(void *this,void *param_1,int param_2)

{
  CFastVB__Unk_00589367((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
