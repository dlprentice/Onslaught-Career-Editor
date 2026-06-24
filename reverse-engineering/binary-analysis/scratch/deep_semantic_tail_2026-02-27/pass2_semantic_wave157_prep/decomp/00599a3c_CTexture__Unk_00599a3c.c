/* address: 0x00599a3c */
/* name: CTexture__Unk_00599a3c */
/* signature: void * __thiscall CTexture__Unk_00599a3c(void * this, void * param_1, int param_2) */


void * __thiscall CTexture__Unk_00599a3c(void *this,void *param_1,int param_2)

{
  CTexture__Helper_00599831(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
