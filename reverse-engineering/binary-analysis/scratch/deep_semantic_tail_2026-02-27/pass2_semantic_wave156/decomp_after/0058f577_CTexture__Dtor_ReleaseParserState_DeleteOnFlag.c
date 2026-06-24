/* address: 0x0058f577 */
/* name: CTexture__Dtor_ReleaseParserState_DeleteOnFlag */
/* signature: void * __thiscall CTexture__Dtor_ReleaseParserState_DeleteOnFlag(void * this, void * param_1, int param_2) */


void * __thiscall
CTexture__Dtor_ReleaseParserState_DeleteOnFlag(void *this,void *param_1,int param_2)

{
  CTexture__Helper_0058f331((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
