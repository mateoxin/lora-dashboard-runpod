import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcessesTabComponent } from './processes-tab.component';

describe('ProcessesTabComponent', () => {
  let component: ProcessesTabComponent;
  let fixture: ComponentFixture<ProcessesTabComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcessesTabComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ProcessesTabComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
