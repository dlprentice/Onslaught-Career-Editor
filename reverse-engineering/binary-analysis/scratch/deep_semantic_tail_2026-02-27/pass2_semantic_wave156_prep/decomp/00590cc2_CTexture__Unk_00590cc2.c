/* address: 0x00590cc2 */
/* name: CTexture__Unk_00590cc2 */
/* signature: void * __thiscall CTexture__Unk_00590cc2(void * this, void * param_1, int param_2) */


void * __thiscall CTexture__Unk_00590cc2(void *this,void *param_1,int param_2)

{
  CTexture__Unk_00590c4a(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
