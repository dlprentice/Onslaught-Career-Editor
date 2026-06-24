/* address: 0x0058f1e0 */
/* name: CTexture__Unk_0058f1e0 */
/* signature: void * __thiscall CTexture__Unk_0058f1e0(void * this, void * param_1, int param_2) */


void * __thiscall CTexture__Unk_0058f1e0(void *this,void *param_1,int param_2)

{
  CTexture__Helper_0058fb70(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
