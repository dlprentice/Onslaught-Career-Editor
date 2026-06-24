/* address: 0x004f3a50 */
/* name: CCSPersistentThing__VFunc_01_004f3a50 */
/* signature: void * __thiscall CCSPersistentThing__VFunc_01_004f3a50(void * this, void * param_1, int param_2) */


void * __thiscall CCSPersistentThing__VFunc_01_004f3a50(void *this,void *param_1,int param_2)

{
  CThing__Unk_004f3a70((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
