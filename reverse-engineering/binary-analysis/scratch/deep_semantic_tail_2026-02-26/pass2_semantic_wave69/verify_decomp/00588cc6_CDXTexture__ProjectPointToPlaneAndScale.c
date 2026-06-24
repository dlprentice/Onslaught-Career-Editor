/* address: 0x00588cc6 */
/* name: CDXTexture__ProjectPointToPlaneAndScale */
/* signature: void __stdcall CDXTexture__ProjectPointToPlaneAndScale(void * param_1, void * param_2, void * param_3, float param_4, void * param_5) */


void CDXTexture__ProjectPointToPlaneAndScale
               (void *param_1,void *param_2,void *param_3,float param_4,void *param_5)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;

  *(undefined4 *)param_5 = *(undefined4 *)param_1;
  *(undefined4 *)((int)param_5 + 4) = *(undefined4 *)((int)param_1 + 4);
  *(undefined4 *)((int)param_5 + 8) = *(undefined4 *)((int)param_1 + 8);
  *(float *)param_5 = *(float *)param_5 - *(float *)param_2;
  *(float *)((int)param_5 + 4) = *(float *)((int)param_5 + 4) - *(float *)((int)param_2 + 4);
  fVar3 = *(float *)((int)param_5 + 8) - *(float *)((int)param_2 + 8);
  *(float *)((int)param_5 + 8) = fVar3;
  fVar4 = *(float *)((int)param_5 + 4) * *(float *)((int)param_3 + 4) +
          *(float *)param_3 * *(float *)param_5 + fVar3 * *(float *)((int)param_3 + 8);
  fVar1 = *(float *)param_3;
  fVar2 = *(float *)((int)param_3 + 4);
  *(float *)((int)param_5 + 8) = fVar3 - fVar4 * *(float *)((int)param_3 + 8);
  fVar1 = (*(float *)param_5 - fVar4 * fVar1) * param_4;
  *(float *)param_5 = fVar1;
  fVar2 = (*(float *)((int)param_5 + 4) - fVar4 * fVar2) * param_4;
  *(float *)((int)param_5 + 4) = fVar2;
  *(float *)((int)param_5 + 8) = param_4 * *(float *)((int)param_5 + 8);
  *(float *)param_5 = fVar1 + *(float *)param_2;
  *(float *)((int)param_5 + 4) = fVar2 + *(float *)((int)param_2 + 4);
  *(float *)((int)param_5 + 8) = *(float *)((int)param_2 + 8) + *(float *)((int)param_5 + 8);
  return;
}
