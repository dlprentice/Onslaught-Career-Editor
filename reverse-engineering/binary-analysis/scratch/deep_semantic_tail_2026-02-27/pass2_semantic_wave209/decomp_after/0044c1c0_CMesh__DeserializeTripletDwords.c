/* address: 0x0044c1c0 */
/* name: CMesh__DeserializeTripletDwords */
/* signature: void __thiscall CMesh__DeserializeTripletDwords(void * this, void * param_1, int param_2) */


void __thiscall CMesh__DeserializeTripletDwords(void *this,void *param_1,int param_2)

{
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)this = param_1;
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)((int)this + 4) = param_1;
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)((int)this + 8) = param_1;
  return;
}
