/* address: 0x004539b0 */
/* name: CControllerDefinition__VFunc_00_004539b0 */
/* signature: void * __thiscall CControllerDefinition__VFunc_00_004539b0(void * this, void * param_1, int param_2) */


void * __thiscall CControllerDefinition__VFunc_00_004539b0(void *this,void *param_1,int param_2)

{
  CControllerDefinition__ctor_like_004539d0(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
