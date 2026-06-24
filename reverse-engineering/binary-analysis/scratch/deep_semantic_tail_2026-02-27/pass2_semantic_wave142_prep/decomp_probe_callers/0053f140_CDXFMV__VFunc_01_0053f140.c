/* address: 0x0053f140 */
/* name: CDXFMV__VFunc_01_0053f140 */
/* signature: void * __thiscall CDXFMV__VFunc_01_0053f140(void * this, void * param_1, int param_2) */


void * __thiscall CDXFMV__VFunc_01_0053f140(void *this,void *param_1,int param_2)

{
  CVBufTexture__Unk_0053f0a0(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
